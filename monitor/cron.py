from monitor.atlassian_monitoring.atlassian_monitor import AtlassianMonitor


def monitor():
    atl = AtlassianMonitor()
    atl.jira_monitoring()
    #atl.confluence_monitoring()
    #atl.check_and_update_issues()
    #atl.move_page()

    #with open('/sample.txt', 'a') as f:
    #    for i in processed:
    #        f.write(f'{i.issue_url}\n')
    #    f.close()
