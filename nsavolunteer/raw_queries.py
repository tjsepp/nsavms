bad_familyAgg_records ="""
SELECT
family,
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
where totalHoursSum<>totHoursFromAgg
"""


FAMILY_DATA_CONSOLIDATED = """
SELECT
name,
'Volunteer' as Type,
Family as family,
familyname,
sc.schoolYear as year,
evt.eventName,
volunteerDate,
volunteerHours
FROM
volunteerHours vh
join familyProfile fp
	on fp.FamilyProfileId = vh.family
join authtools_user au
	on au.id = volunteer
join schoolYear sc
	on vh.SchoolYear = sc.yearId
join nsaEvents evt
	on evt.eventId = vh.event
where vh.approved = 1
and sc.currentYear = 1
and FamilyProfileId =%s
Union all
SELECT
name,
'Traffic' as Type,
Relatedfamily as family,
familyname,
sc.schoolYear as year,
'Traffic Duty',
trafficDutyWeekEnd,
volunteerHours
FROM
traffic_Duty vh
join familyProfile fp
	on fp.FamilyProfileId = vh.relatedfamily
join authtools_user au
	on au.id = volunteer
join schoolYear sc
	on vh.SchoolYear = sc.yearId
where FamilyProfileId =%s
and sc.currentYear = 1
Union all
SELECT
name,
'Reward Card' as Type,
Relatedfamily as family,
familyname,
sc.schoolYear as year,
'King Soopers',
refillDate,
volunteerHours
FROM
rewardCardData vh
join familyProfile fp
	on fp.FamilyProfileId = vh.relatedfamily
join authtools_user au
	on au.id = volunteer
join schoolYear sc
	on vh.SchoolYear = sc.yearId
where FamilyProfileId =%s
and sc.currentYear = 1
order by 4,5,1,2
"""

currentVsPriorYear = """
SELECT
yearName,
sum(volunteerHours) as totalHours
FROM
(
	SELECT
    vh.*,
    sy.schoolYear as yearName
    FROM
    volunteerHours vh
    Join schoolYear sy
    	on vh.SchoolYear = sy.yearId
    where
    vh.schoolYear = 3
    and volunteerDate <=DATE_ADD(CURRENT_DATE,INTERVAL -1 YEAR)
    Union
    SELECT
    vh.*,
    sy.schoolYear as yearName
    FROM
    volunteerHours vh
    Join schoolYear sy
    	on vh.SchoolYear = sy.yearId
    where
    vh.schoolYear = 4
    and volunteerDate <=CURRENT_DATE
) agg
group by yearName
"""


DASHBOARD_FAMILY_TOTALS='''
SELECT
fp.FamilyProfileId,
fp.familyName,
fp.trafficReq,
fp.volunteerReq,
fa.schoolYear,
volHrs.volunteerHours,
pndHrs.pendingHours,
rwcard.rewardCardHours,
rwcard.rewardCardValue,
tr.trafficDutyHours,
tr.totalShifts,
ifnull(volHrs.volunteerHours,0)+ifnull(rwcard.rewardCardHours,0)+ifnull(tr.trafficDutyHours,0) as totalHours
FROM
familyProfile fp
join familyAggregate fa
	on fp.FamilyProfileId = fa.relatedFamily
    and fa.schoolYear = (select yearId from schoolYear where currentYear = 1)
Left join
	( select
         family,
         schoolYear,
         sum(volunteerHours) as volunteerHours
     from
     	volunteerHours
     where approved = 1

     group by family,schoolYear) volHrs
     on fp.FamilyProfileId = volHrs.family
     and volHrs.schoolYear = fa.schoolYear
left join
	(select
            family,
            schoolYear,
            sum(volunteerHours) as pendingHours
     	from
      		volunteerHours
     	where approved = 0
     	group by family,schoolYear) pndHrs
        	on pndHrs.family = fp.FamilyProfileId
            and pndHrs.schoolYear = fa.SchoolYear
left join(
    select
            relatedFamily,
            schoolYear,
            sum(volunteerHours) as rewardCardHours,
            sum(refillValue) as rewardCardValue
    	from
    		rewardCardData
    	group by relatedFamily,schoolYear) rwcard
        on  rwcard.relatedFamily = fp.FamilyProfileId
        and rwcard.schoolYear = fa.SchoolYear
left join(
    	select
    		relatedFamily,
    		schoolYear,
    		sum(volunteerHours) as trafficDutyHours,
    		sum(totalTrafficShifts) as totalShifts
    	from
    		traffic_Duty
    	group by
    		relatedFamily,schoolYear) tr
            	on  tr.relatedFamily = fp.FamilyProfileId
                and tr.schoolYear = fa.SchoolYear

where
fp.familyProfileId in (select familyprofile_id from familyVolunteers where user_id = %s)
'''

DASHBOARD_VOLUNTEER_DATA ='''
select
fp.familyName,
vp.firstName,
hrs.*
from
(
	select
	vh.volunteer,
	vh.family,
	schoolYear,
	vh.volunteerDate as volDate,
	ev.eventName as hrsType,
	vh.task,
	vh.volunteerHours,
	case
	when vh.approved = 1
		then 'Yes'
		else 'No'
	end as approved
	from
	volunteerHours vh
	join nsaEvents ev
		ON vh.event = ev.eventId
UNION
	select
	td.volunteer,
	td.relatedfamily,
	schoolYear,
	td.trafficDutyWeekEnd as volDate,
	'Traffic Duty' as hrsType,
	'' as task,
	volunteerHours,
	'Yes' as approved
	from
	traffic_Duty td
union
	select
	volunteer,
	relatedFamily,
	schoolYear,
	refilldate  as volDate,
	'King Soopers Purchase' as hrsType,
	'' as task,
	volunteerHours,
	'Yes' as approved
	from
	rewardCardData rd
) hrs
join familyProfile fp
	on fp.FamilyProfileId = hrs.family
join volunteerProfile vp
	  on vp.linkedUserAccount_id = hrs.volunteer
where
family in (select familyprofile_id from familyVolunteers where user_id = %s)
and schoolYear=%s
order by voldate desc
'''