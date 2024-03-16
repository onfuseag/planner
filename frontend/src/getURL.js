import { webserver_port } from '../../../../sites/common_site_config.json'

export function getURL() {
    let host = window.location.hostname
    let siteName = window.site_name
    let port = window.location.port ? `:${webserver_port}` : ''
    let protocol = port ? 'http' : 'https'
    let url = `${protocol}://${host}${port}`

    return url;
}