import pycurl, time
c = pycurl.Curl()
#website='https://technixmw.com'
#c.setopt(c.VERBOSE, False) # to see request details
ts = time.clock()
def tcp_timings(website,cipher):
    website = 'https://www.{0}'.format(website)
    c.setopt(pycurl.WRITEFUNCTION, lambda x: None) ##hide data
    #response = requests.get(website)
    c.setopt(c.URL, website)
    c.setopt(c.SSL_CIPHER_LIST, cipher);
    c.perform()
    tcp_timings = {}
    tcp_timings['domain'] = c.getinfo(pycurl.EFFECTIVE_URL)
    tcp_timings['IPAddress'] = c.getinfo(pycurl.PRIMARY_IP)
    tcp_timings['Port'] = c.getinfo(pycurl.PRIMARY_PORT)
    tcp_timings['negotiated-cipher']=cipher
    tcp_timings['DNST'] = c.getinfo(pycurl.NAMELOOKUP_TIME)
    tcp_timings['SSLT'] = c.getinfo(pycurl.APPCONNECT_TIME)
    tcp_timings['TCPT'] = c.getinfo(pycurl.CONNECT_TIME)
    tcp_timings['TTFB'] = c.getinfo(pycurl.PRETRANSFER_TIME)
    tcp_timings['redirect'] = c.getinfo(pycurl.REDIRECT_TIME)
    tcp_timings['starttransfer'] = c.getinfo(pycurl.STARTTRANSFER_TIME)
    tcp_timings['total-time'] = c.getinfo(pycurl.TOTAL_TIME)
    tcp_timings['http-code'] = c.getinfo(pycurl.HTTP_CODE)
    tcp_timings['redirect-count'] = c.getinfo(pycurl.REDIRECT_COUNT)
    tcp_timings['size-upload'] = c.getinfo(pycurl.SIZE_UPLOAD)
    tcp_timings['size-download'] = c.getinfo(pycurl.SIZE_DOWNLOAD)
    tcp_timings['header-size'] = c.getinfo(pycurl.HEADER_SIZE)
    tcp_timings['request-size'] = c.getinfo(pycurl.REQUEST_SIZE)
    tcp_timings['content-length-download'] = c.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD)
    tcp_timings['content-length-upload'] = c.getinfo(pycurl.CONTENT_LENGTH_UPLOAD)
    #tcp_timings['content-type'] = c.getinfo(pycurl.CONTENT_TYPE)
    #tcp_timings['response-code'] = c.getinfo(pycurl.RESPONSE_CODE)
    #tcp_timings['Protocol'] = c.getinfo(pycurl.PROTOCOL)
    #tcp_timings['certificate-info'] = c.getinfo(pycurl.INFO_CERTINFO)
    #tcp_timings['filetime'] = c.getinfo(pycurl.INFO_FILETIME)
    #tcp_timings['starttransfer-time'] = c.getinfo(pycurl.STARTTRANSFER_TIME)
    #tcp_timings['redirect-time'] = c.getinfo(pycurl.REDIRECT_TIME)
    #tcp_timings['redirect-count'] = c.getinfo(pycurl.REDIRECT_COUNT)
    #tcp_timings['http-connectcode'] = c.getinfo(pycurl.HTTP_CONNECTCODE)
    # tcp_timings['httpauth-avail'] = c.getinfo(pycurl.HTTPAUTH_AVAIL)
    # tcp_timings['proxyauth-avail'] = c.getinfo(pycurl.PROXYAUTH_AVAIL)
    # tcp_timings['os-errno'] = c.getinfo(pycurl.OS_ERRNO)
    #tcp_timings['num-connects'] = c.getinfo(pycurl.NUM_CONNECTS)
    #tcp_timings['ssl-engines'] = c.getinfo(pycurl.SSL_ENGINES)
    # tcp_timings['cookielist'] = c.getinfo(pycurl.INFO_COOKIELIST)
    # tcp_timings['lastsocket'] = c.getinfo(pycurl.LASTSOCKET)
    # tcp_timings['ftp-entry-path'] = c.getinfo(pycurl.FTP_ENTRY_PATH)
    #print(response.text)
    return tcp_timings

if __name__ == "__main__":
    hello=tcp_timings('technixmw.com','TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA')
    print(hello)





