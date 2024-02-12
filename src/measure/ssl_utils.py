import socket
import ssl
def get_sslinfo(website):
    context = ssl.create_default_context()
    context.set_alpn_protocols(['quic','http/2','http/1.1','spdy/2','http/3'])
    with socket.create_connection((website, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=website) as ssock:
            cert_info={}
            #cert_info['ssl-version']=ssock.version()
            cert_info['negotiated-cipher']=ssock.cipher()
            #cert_info['shared-ciphers']=ssock.shared_ciphers()
            cert_info['negotiated-protocol']=ssock.selected_alpn_protocol()
    return cert_info

if __name__ == "__main__":
    sslinfo=get_sslinfo('google.com')
    print(sslinfo)

