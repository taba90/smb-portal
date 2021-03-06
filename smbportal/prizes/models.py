#########################################################################
#
# Copyright 2019, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

import datetime as dt
import logging

from django.db import connections
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.db.models import Union
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from smbbackend import calculateprizes
import pytz

from base.fields import ChoiceArrayField
from profiles.models import EndUserProfile

logger = logging.getLogger(__name__)


class Sponsor(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("sponsor")
    )
    logo = models.ImageField(
        verbose_name="logo",
        null=True,
        blank=True,
    )
    url = models.URLField(
        verbose_name=_("url"),
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Prize(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("name"),
    )
    image = models.ImageField(
        verbose_name="image",
        null=True,
        blank=True,
    )
    description = models.TextField(
        verbose_name=_("description"),
        blank=True
    )
    sponsor = models.ForeignKey(
        "Sponsor",
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("sponsor"),
    )
    url = models.URLField(
        verbose_name=("url"),
        null=True,
        blank=True,
        help_text=_(
            "URL where more information about this prize can be obtained")
    )

    class Meta:
        ordering = (
            "name",
        )

    def __str__(self):
        return self.name


class CompetitionPrize(models.Model):
    prize = models.ForeignKey(
        "Prize",
        on_delete=models.CASCADE,
        verbose_name=_("prize"),
    )
    competition = models.ForeignKey(
        "Competition",
        on_delete=models.CASCADE,
        verbose_name=_("competition")
    )
    user_rank = models.IntegerField(
        verbose_name=_("user rank"),
        null=True,
        blank=True,
        help_text=_(
            "Rank that the user must attain in the underlying competition in "
            "order to be awarded the prize. If None, all of the competition'"
            "s winners will be awarded the prize"
        )
    )
    prize_attribution_template = models.TextField(
        verbose_name=_("prize attribution template"),
        help_text=_(
            "Message shown to the user when the prize is won. This string is "
            "treated as a normal django template and rendered with a context "
            "that has the following variables: `score`, `rank`. The "
            "`django.contrib.humanize` is available. Example: The string "
            "'Congratulations, you got {{ rank|ordinal }} place with a score "
            "of {{ score }}' would get rendered as 'Congratulations, you got "
            "1st place with a score of 2061'"),
        blank=True
    )

    class Meta:
        ordering = (
            "prize",
            "competition",
            "user_rank",
        )

    def __str__(self):
        return "{} - {} - (rank {})".format(
            self.competition, self.prize, self.user_rank)


class CurrentCompetitionManager(models.Manager):

    def get_queryset(self):
        now = dt.datetime.now(pytz.utc)
        return super().get_queryset().filter(
            start_date__lte=now, end_date__gte=now)


class FinishedCompetitionManager(models.Manager):

    def get_queryset(self):
        now = dt.datetime.now(pytz.utc)
        return super().get_queryset().filter(end_date__lte=now)


class Competition(models.Model):
    """Stores the result of a competition"""

    CRITERIUM_SAVED_SO2_EMISSIONS = "saved SO2 emissions"
    CRITERIUM_SAVED_NOX_EMISSIONS = "saved NOx emissions"
    CRITERIUM_SAVED_CO2_EMISSIONS = "saved CO2 emissions"
    CRITERIUM_SAVED_CO_EMISSIONS = "saved CO emissions"
    CRITERIUM_SAVED_PM10_EMISSIONS = "saved PM10 emissions"
    CRITERIUM_CONSUMED_CALORIES = "consumed calories"
    CRITERIUM_BIKE_USAGE_FREQUENCY = "bike usage frequency"
    CRITERIUM_PUBLIC_TRANSPORT_USAGE_FREQUENCY = (
        "public transport usage frequency")
    CRITERIUM_BIKE_DISTANCE = "bike distance"
    CRITERIUM_SUSTAINABLE_MEANS_DISTANCE = "sustainable means distance"

    name = models.CharField(
        verbose_name=_("name"),
        max_length=100
    )
    description = models.TextField(
        verbose_name=_("description"),
        blank=True
    )
    age_groups = ChoiceArrayField(
        base_field=models.CharField(
            max_length=10,
            choices=[
                (
                    EndUserProfile.AGE_YOUNGER_THAN_NINETEEN,
                    _("< 19")
                ),
                (
                    EndUserProfile.AGE_BETWEEN_NINETEEN_AND_THIRTY,
                    _("19 - 30")
                ),
                (
                    EndUserProfile.AGE_BETWEEN_THIRTY_AND_SIXTY_FIVE,
                    _("30 - 65")
                ),
                (
                    EndUserProfile.AGE_OLDER_THAN_SIXTY_FIVE,
                    _("65+")
                ),
            ]
        ),
        size=4,
        verbose_name=_("age group"),
        default=list
    )
    start_date = models.DateTimeField(
        verbose_name=_("start date"),
        help_text=_("Date when the competition started"),
    )
    end_date = models.DateTimeField(
        verbose_name=_("end date"),
        help_text=_("Date when the competition ended"),
    )
    criteria = ChoiceArrayField(
        base_field=models.CharField(
            max_length=100,
            choices=[
                (CRITERIUM_SAVED_SO2_EMISSIONS, _("saved SO2 emissions")),
                (CRITERIUM_SAVED_NOX_EMISSIONS, _("saved NOx emissions")),
                (CRITERIUM_SAVED_CO2_EMISSIONS, _("saved CO2 emissions")),
                (CRITERIUM_SAVED_CO_EMISSIONS, _("saved CO emissions")),
                (CRITERIUM_SAVED_PM10_EMISSIONS, _("saved PM10 emissions")),
                # NOTE: The following are commented out because the backend
                # does not know how to score them yet
                #
                # (CRITERIUM_CONSUMED_CALORIES, _("consumed calories")),
                # (CRITERIUM_BIKE_USAGE_FREQUENCY, _("bike usage frequency")),
                # (
                #     CRITERIUM_PUBLIC_TRANSPORT_USAGE_FREQUENCY,
                #     _("public transport usage frequency")
                # ),
                # (CRITERIUM_BIKE_DISTANCE, _("bike distance")),
                # (
                #     CRITERIUM_SUSTAINABLE_MEANS_DISTANCE,
                #     _("sustainable means distance")
                # ),
            ]
        ),
        verbose_name=_("criteria"),
        help_text=_(
            "Which criteria will be used for deciding who wins the "
            "competition"
        )
    )
    winner_threshold = models.IntegerField(
        verbose_name=_("winner threshold"),
        default=1,
        help_text=_(
            "After results are calculated and ordered, how many of the top "
            "users should be considered winners? The winners will earn the "
            "prizes specified in this competition."
        )
    )
    closing_leaderboard = JSONField(
        verbose_name=_("closing leaderboard"),
        null=True,
        blank=True,
        help_text=_(
            "leaderboard calculated at the time the competition was closed. "
            "Winners are assigned from the score in this leaderboard"
        )
    )
    sponsors = models.ManyToManyField(
        "Sponsor",
        blank=True,
        help_text=_("Sponsors for the competition")
    )
    regions = models.ManyToManyField(
        "RegionOfInterest",
        blank=True,
        help_text=_("Regions of interest for the competition, if any")
    )

    objects = models.Manager()
    current_competitions_manager = CurrentCompetitionManager()

    class Meta:
        ordering = (
            "name",
            "start_date",
            "end_date",
            "age_groups",
        )

    def __str__(self):
        return "Competition {!r} ({} - {})".format(
            self.name,
            self.start_date.strftime("%Y-%m-%d"),
            self.end_date.strftime("%Y-%m-%d")
        )

    def is_open(self):
        now = dt.datetime.now(pytz.utc)
        return (now > self.start_date) and (now <= self.end_date)

    def get_leaderboard(self):
        if self.is_open():
            leaderboard = calculateprizes.get_leaderboard(
                self.as_competition_info(),
                connections["default"].connection.cursor()
            )
        else:
            leaderboard = self.closing_leaderboard or []
        user_model = get_user_model()
        result = []
        for entry in leaderboard:
            try:
                user = user_model.objects.get(id=entry["user"])
            except user_model.DoesNotExist:
                logger.warning(f"Cannot find user {entry['user']} in the DB")
            else:
                result.append((user, entry["criteria_points"]))
        return result

    def as_competition_info(self):
        roi = self.regions.aggregate(roi=Union("geom"))["roi"]
        return calculateprizes.CompetitionInfo(
            id=self.id,
            name=self.name,
            criteria=self.criteria,
            winner_threshold=self.winner_threshold,
            start_date=self.start_date,
            end_date=self.end_date,
            age_groups=self.age_groups,
            region_of_interest=roi
        )


class CurrentCompetition(Competition):

    objects = CurrentCompetitionManager()

    class Meta:
        proxy = True


class FinishedCompetition(Competition):

    objects = FinishedCompetitionManager()

    class Meta:
        proxy = True


class CompetitionParticipant(models.Model):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_MODERATION = "pending_moderation"

    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "profiles.SmbUser",
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="competitions_participating"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    registration_status = models.CharField(
        max_length=100,
        choices=[
            (
                APPROVED,
                _("approved")
            ),
            (
                REJECTED,
                _("rejected")
            ),
            (
                PENDING_MODERATION,
                _("pending moderation")
            ),
        ]
    )
    registration_justification = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "A justification for the moderation of the user's request. Mostly "
            "useful as a means to let the user know why its participation "
            "request was rejected."
        )
    )

    def get_score(self):
        if self.registration_status == self.APPROVED:
            result = calculateprizes.get_user_score(
                self.competition.as_competition_info(),
                self.user.pk,
                connections["default"].connection.cursor()
            )
        else:
            result = {}
        return result


class PendingCompetitionParticipantManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            registration_status=CompetitionParticipant.PENDING_MODERATION)


class PendingCompetitionParticipant(CompetitionParticipant):

    objects = PendingCompetitionParticipantManager()

    class Meta:
        proxy = True


class Winner(models.Model):
    """Stores the winners of competitions"""
    rank = models.IntegerField(
        verbose_name=_("rank"),
    )
    participant = models.ForeignKey(
        CompetitionParticipant,
        on_delete=models.CASCADE,
        limit_choices_to={
            "registration_status": CompetitionParticipant.APPROVED
        }
    )

    class Meta:
        ordering = (
            "rank",
            "participant",
        )

    def __str__(self):
        return "Competition {!r} ({} - {})".format(
            self.participant.competition.name,
            self.participant.user.username,
            self.rank
        )


class RegionOfInterest(gismodels.Model):
    name = models.CharField(max_length=200)
    geom = gismodels.PolygonField(
        verbose_name=_("geometry"),
    )

    def __str__(self):
        return self.name
