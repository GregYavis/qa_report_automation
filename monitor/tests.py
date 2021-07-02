import json

data = '{"timestamp": 1625206146397, "webhookEvent": "jira:issue_updated", "issue_event_type_name": ' \
       '"issue_updated", "user": {"self": "https://jira.4slovo.ru/rest/api/2/user?username=m.pohilyj", ' \
       '"name": "m.pohilyj", "key": "m.pohilyj", "emailAddress": "m.pohilyj@4slovo.ru", "avatarUrls": ' \
       '{"48x48": "https://jira.4slovo.ru/secure/useravatar?avatarId=10338", "24x24": ' \
       '"https://jira.4slovo.ru/secure/useravatar?size=small&avatarId=10338", "16x16": ' \
       '"https://jira.4slovo.ru/secure/useravatar?size=xsmall&avatarId=10338", "32x32": ' \
       '"https://jira.4slovo.ru/secure/useravatar?size=medium&avatarId=10338"}, "displayName": ' \
       '"Михаил А. Похилый", "active": True, "timeZone": "Europe/Moscow"}, "issue": {"id": "23254", ' \
       '"self": "https://jira.4slovo.ru/rest/api/2/issue/23254", "key": "SLOV-7020", "fields": {"customfield_15401": ' \
       'None, "customfield_11320": None, "fixVersions": [{"self": "https://jira.4slovo.ru/rest/api/2/version/14955", "' \
       'id": "14955", "description": "", "name": "kz.3.23.1", "archived": False, "released": False}], "resolution":' \
       ' None, "customfield_15403": None, "customfield_11314": None, "customfield_11315": None, "customfield_11316":' \
       ' None, "customfield_11317": None, "customfield_11318": None, "customfield_10900": None, "customfield_10901":' \
       ' None, "customfield_11319": None, "customfield_10902": [], "customfield_10903": None, "customfield_10904": ' \
       'None, "customfield_10905": None, "customfield_10906": None, "lastViewed": "2021-07-02T09:02:24.687+0300", ' \
       '"customfield_10100": None, "customfield_11310": None, "priority": ' \
       '{"self": "https://jira.4slovo.ru/rest/api/2/priority/10000", "iconUrl": ' \
       '"https://jira.4slovo.ru/images/icons/priorities/critical.svg", "name": "' \
       'Critical", "id": "10000"}, "customfield_11311": None, "customfield_11312":' \
       ' None, "labels": [], "customfield_11313": None, "customfield_11303": None, ' \
       '"customfield_11304": None, "customfield_11305": None, "customfield_11306": ' \
       'None, "customfield_11307": None, "timeestimate": None, "aggregatetimeoriginalestimate":' \
       ' None, "customfield_11308": None, "versions": [], "customfield_11309": None, "issuelinks": ' \
       '[], "assignee": {"self": "https://jira.4slovo.ru/rest/api/2/user?username=a.portnov", "name":' \
       ' "a.portnov", "key": "a.portnov", "emailAddress": "a.portnov@4slovo.ru", "avatarUrls": {"48x48": ' \
       '"https://jira.4slovo.ru/secure/useravatar?avatarId=10341", "24x24":' \
       ' "https://jira.4slovo.ru/secure/useravatar?size=small&avatarId=10341", ' \
       '"16x16": "https://jira.4slovo.ru/secure/useravatar?size=xsmall&avatarId=10341", "32x32": ' \
       '"https://jira.4slovo.ru/secure/useravatar?size=medium&avatarId=10341"}, "displayName": ' \
       '"Алексей Ю. Портнов", "active": True, "timeZone": "Europe/Moscow"}, "status": {"self": ' \
       '"https://jira.4slovo.ru/rest/api/2/status/1", "description": ' \
       '"The issue is open and ready for the assignee to start work on it.", "iconUrl": ' \
       '"https://jira.4slovo.ru/images/icons/statuses/open.png", "name": "Open", "id": "1", "statusCategory": ' \
       '{"self": "https://jira.4slovo.ru/rest/api/2/statuscategory/2", "id": 2, "key": "new", "colorName": "blue-gray", ' \
       '"name": "To Do"}}, "components": [], "customfield_13200": ' \
       '"{summaryBean=com.atlassian.jira.plugin.devstatus.rest.SummaryBean@803c995[summary=' \
       '{pullrequest=com.atlassian.jira.plugin.devstatus.rest.SummaryItemBean@6fd09fa7[overall=PullRequestOverallBean{stateCount=0,' \
       ' state=\"OPEN\", details=PullRequestOverallDetails{openCount=0, mergedCount=0, declinedCount=0}},byInstanceType={}], ' \
       'build=com.atlassian.jira.plugin.devstatus.rest.SummaryItemBean@140f47d9[overall=com.atlassian.jira.plugin.' \
       'devstatus.summary.beans.BuildOverallBean@7f49df58[failedBuildCount=0,successfulBuildCount=0,unknownBuildCount=' \
       '0,count=0,lastUpdated=<null>,lastUpdatedTimestamp=<null>],byInstanceType={}], review=com.atlassian.jira.plugin.' \
       'devstatus.rest.SummaryItemBean@3f246daa[overall=com.atlassian.jira.plugin.devstatus.summary.beans.ReviewsOverall' \
       'Bean@e88a668[stateCount=0,state=<null>,dueDate=<null>,overDue=false,count=0,lastUpdated=<null>,lastUpdatedTimest' \
       'amp=<null>],byInstanceType={}], deployment-environment=com.atlassian.jira.plugin.devstatus.rest.SummaryItemBean' \
       '@605709ef[overall=com.atlassian.jira.plugin.devstatus.summary.beans.DeploymentOverallBean@5155a9a2[topEnvironme' \
       'nts=[],showProjects=false,successfulCount=0,count=0,lastUpdated=<null>,lastUpdatedTimestamp=<null>],byInstanceT' \
       'ype={}], repository=com.atlassian.jira.plugin.devstatus.rest.SummaryItemBean@4d80c71f[overall=com.atlassian.jir' \
       'a.plugin.devstatus.summary.beans.CommitOverallBean@6f09321[count=0,lastUpdated=<null>,lastUpdatedTimestamp=<nul' \
       'l>],byInstanceType={}], branch=com.atlassian.jira.plugin.devstatus.rest.SummaryItemBean@5e30ea61[overall=com.at' \
       'lassian.jira.plugin.devstatus.summary.beans.BranchOverallBean@225440bc[count=0,lastUpdated=<null>,lastUpdatedTi' \
       'mestamp=<null>],byInstanceType={}]},errors=[],configErrors=[]], devSummaryJson={"cachedValue":{"errors":[],"conf' \
       'igErrors":[],"summary":{"pullrequest":{"overall":{"count":0,"lastUpdated":null,"stateCount":0,"state":"OPEN","de' \
       'tails":{"openCount":0,"mergedCount":0,"declinedCount":0,"total":0},"open":true},"byInstanceType":{}},"build":{"o' \
       'verall":{"count":0,"lastUpdated":null,"failedBuildCount":0,"successfulBuildCount":0,"unknownBuildCount":0},"byIn' \
       'stanceType":{}},"review":{"overall":{"count":0,"lastUpdated":null,"stateCount":0,"state":null,"dueDate":null,"ov' \
       'erDue":false,"completed":false},"byInstanceType":{}},"deployment-environment":{"overall":{"count":0,"lastUpdated' \
       '":null,"topEnvironments":[],"showProjects":false,"successfulCount":0},"byInstanceType":{}},"repository":{"overal' \
       'l":{"count":0,"lastUpdated":null},"byInstanceType":{}},"branch":{"overall":{"count":0,"lastUpdated":null},"byIns' \
       'tanceType":{}}}},"isStale":false}}", "customfield_11300": None, "customfield_11301": None, "customfield_11302":' \
       ' None, "aggregatetimeestimate": None, "creator": {"self": "https://jira.4slovo.ru/rest/api/2/user?username=l.ka' \
       'syanova", "name": "l.kasyanova", "key": "l.kasyanova", "emailAddress": "l.kasyanova@4slovo.kz", "avatarUrls": {' \
       '"48x48": "https://www.gravatar.com/avatar/ea17fe39e31536025f5ff4a426e72896?d=mm&s=48", "24x24": "https://www.gr' \
       'avatar.com/avatar/ea17fe39e31536025f5ff4a426e72896?d=mm&s=24", "16x16": "https://www.gravatar.com/avatar/ea17fe' \
       '39e31536025f5ff4a426e72896?d=mm&s=16", "32x32": "https://www.gravatar.com/avatar/ea17fe39e31536025f5ff4a426e728' \
       '96?d=mm&s=32"}, "displayName": "Людмила Н. Касьянова", "active": True, "timeZone": "Europe/Moscow"}, "subtasks"' \
       ': [], "reporter": {"self": "https://jira.4slovo.ru/rest/api/2/user?username=l.kasyanova", "name": "l.kasyanova"' \
       ', "key": "l.kasyanova", "emailAddress": "l.kasyanova@4slovo.kz", "avatarUrls": {"48x48": "https://www.gravatar.' \
       'com/avatar/ea17fe39e31536025f5ff4a426e72896?d=mm&s=48", "24x24": "https://www.gravatar.com/avatar/ea17fe39e3153' \
       '6025f5ff4a426e72896?d=mm&s=24", "16x16": "https://www.gravatar.com/avatar/ea17fe39e31536025f5ff4a426e72896?d=mm' \
       '&s=16", "32x32": "https://www.gravatar.com/avatar/ea17fe39e31536025f5ff4a426e72896?d=mm&s=32"}, "displayName": ' \
       '"Людмила Н. Касьянова", "active": True, "timeZone": "Europe/Moscow"}, "aggregateprogress": {"progress": 0, "' \
       '4slovo.kz", "avatarUrls": {"48x48": "https://www.gravatar.com/avatar/ea17fe39e31536025f5ff4a426e72896?d=mm&s=48' \
       '", "24x24": "https://www.gravatar.com/avatar/ea17fe39e31536025f5ff4a426e72896?d=mm&s=24", "16x16": "https://www' \
       '.gravatar.com/avatar/ea17fe39e31536025f5ff4a426e72896?d=mm&s=16", "32x32": "https://www.gravatar.com/avatar/ea1' \
       '7fe39e31536025f5ff4a426e72896?d=mm&s=32"}, "displayName": "Людмила Н. Касьянова", "active": True, "timeZone": "' \
       'Europe/Moscow"}, "created": "2021-07-01T18:39:48.720+0300", "size": 476386, "mimeType": "application/pdf", "con' \
       'tent": "https://jira.4slovo.ru/secure/attachment/23152/%D0%94%D0%BE%D0%BF.%D1%81%D0%BE%D0%B3%D0%BB%D0%B0%D1%88%' \
       'D0%B5%D0%BD%D0%B8%D0%B5+%D0%BF%D0%BE+%D0%BF%D1%80%D0%BE%D0%BB%D0%BE%D0%BD%D0%B3%D0%B0%D1%86%D0%B8%D0%B8+1205348' \
       '+%2811%29.pdf"}], "customfield_10009": "BA-9", "summary": "исключение фирменного бланка в форме Дополнительного' \
       ' соглашения на пролонгацию", "customfield_10000": None, "customfield_10001": None, "customfield_10003": None, "' \
       'customfield_10004": None, "customfield_10400": None, "environment": None, "duedate": None, "comment": {"comment' \
       's": [], "maxResults": 0, "total": 0, "startAt": 0}}}, "changelog": {"id": "249508", "items": [{"field": "Fix Ve' \
       'rsion", "fieldtype": "jira", "from": "14823", "fromString": "kz.3.30.0", "to": None, "toString": None}, {"field' \
       '": "Fix Version", "fieldtype": "jira", "from": None, "fromString": None, "to": "14955", "toString": "kz.3.23.1"' \
       '}]}}'
print(json.loads(data))