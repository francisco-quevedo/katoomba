import Confluence, ServiceCatalographer, PublicServiceReporter
from config import confluenceHost, confluenceUser, confluencePass, serviceCatalographerURL

# The Wiki space and top-level page to index each service
# This page will be completely overwritten by the script!
confluenceSpaceKey = 'doc'
confluenceParentTitle = 'Supported Services'

if __name__ == '__main__':
    confluence = Confluence.Server(confluenceHost, confluenceUser, confluencePass)
    pageNameMap = {
        # Any services that are not in BiodiversityCatalogue can be placed here.
        # 'Service Name': 'Wiki Page Title'
        'Rserve': 'Rserve service',
        'WebDAV': 'WebDav_FileSharingService'
    }
    parentId = confluence.getPageId(confluenceSpaceKey, confluenceParentTitle)
    bdc = ServiceCatalographer.ServiceCatalographer(serviceCatalographerURL)
    services = bdc.getServices()
    for service in services:
        serviceId = service.self.split('/')[-1]
        try:
            content = PublicServiceReporter.report(service)
        except PublicServiceReporter.DoNotInclude:
            pass
        else:
            pageName = 'BioVeL Service - %s' % service.name
            print('Publishing %s' % pageName)
            confluence.publish(content, confluenceSpaceKey, pageName, parentId)
            pageNameMap[service.name] = pageName
    content = '<ac:layout>'
    ncols = 3
    assert ncols in (2,3), ncols
    if ncols == 2:
        content += '<ac:layout-section ac:type="two_equal">\n'
    else:
        content += '<ac:layout-section ac:type="three_equal">\n'
    sortedKeys = sorted(pageNameMap, key=str.lower)
    split = (len(pageNameMap) + ncols - 1) // ncols
    for i in range(0, len(sortedKeys), split):
        subKeys = sortedKeys[i:i+split]
        content += '<ac:layout-cell>'
        for serviceName in subKeys:
            content += '''
<ac:structured-macro ac:name="panel">
  <ac:parameter ac:name="bgColor">#f3ffac</ac:parameter>
  <ac:parameter ac:name="borderWidth">2</ac:parameter>
  <ac:parameter ac:name="borderStyle">solid</ac:parameter>
  <ac:parameter ac:name="borderColor">#cccc66</ac:parameter>
  <ac:rich-text-body>
    <p><b>
      <ac:link>
        <ri:page ri:content-title="%s" />
          <ac:plain-text-link-body><![CDATA[%s]]></ac:plain-text-link-body>
      </ac:link>
    </b></p>
  </ac:rich-text-body>
</ac:structured-macro>''' % (pageNameMap[serviceName], serviceName)
        content += '</ac:layout-cell>\n'
    content += '</ac:layout-section>\n'
    content += '''<ac:layout-section ac:type="single">
    <ac:layout-cell>
    <p>To find additional services, search in <ac:structured-macro ac:name="biodivcat"></ac:structured-macro>.</p>
    </ac:layout-cell>
    </ac:layout-section>
'''
    content += '</ac:layout>\n'

    print('Publishing %s' % confluenceParentTitle)
    confluence.publish(content, confluenceSpaceKey, confluenceParentTitle, confluence.getPageId(confluenceSpaceKey, 'Start'))
