bad_familyAgg_records ="""
SELECT
ls.familyName,
sy.schoolYear,
totalHoursSum,
totHoursFromAgg
from(
SELECT
family,
fp.familyName,
ix.schoolYear,
sum(totalHrs) as totalHoursSum,
ag.totalVolunteerHours as totHoursFromAgg
from(
   SELECT
    family,
    schoolYear,
    sum(volunteerHours) as totalHrs
    from(
    SELECT
    family,
    schoolYear,
    volunteerHours
    FROM
    volunteerHours
    where approved = 1) ix
    group by family,schoolYear
    union all
    SELECT
    relatedFamily as family,
    schoolYear,
    sum(volunteerHours) as totalHrs
    from(
        SELECT
        relatedFamily,
        schoolYear,
        volunteerHours
        FROM
        traffic_Duty
    ) ix
    group by relatedFamily,schoolYear
    union all
    SELECT
    relatedFamily as family,
    schoolYear,
    sum(volunteerHours) as totalHrs
    from(
        SELECT
        relatedFamily,
        schoolYear,
        volunteerHours
        FROM
        rewardCardData
    ) ix
    group by relatedFamily,schoolYear
)ix
join familyProfile fp
	on fp.FamilyProfileId = ix.family
join familyAggregate ag
	on ag.relatedFamily = ix.family
    and ag.schoolYear = ix.schoolYear
group by family,fp.familyName,ix.schoolYear
) ls
join schoolYear sy
on sy.yearId = ls.schoolYear
where totalHoursSum<>totHoursFromAgg """