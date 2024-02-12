/*
 * Copyright 2019 Princeton University
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 * Author: Kevin Borgolte <borgolte@cs.princeton.edu>
 *         Paul Schmitt <pschmitt@cs.princeton.edu>
 */

#ifndef DNS_DOT_DOH_CLIENT_H
#define DNS_DOT_DOH_CLIENT_H

#include <map>

#include "ns3/application.h"
#include "ns3/ptr.h"

#include "ns3/dnsdotdoh-common.h"

namespace ns3 {
	class EventId;
	class Ipv4Address;
	class Packet;
	class Socket;

	class DnsDotDohClient : public Application {
	public:
		static TypeId GetTypeId(void);

		DnsDotDohClient();
		virtual ~DnsDotDohClient();

		void SetRequests(std::list<DnsDotDohRequest> requests);

	protected:
		virtual void DoDispose(void);

	private:
		virtual void StartApplication(void);
		virtual void StopApplication(void);

		void Send(void);

		void TlsSendClientHello(void);
		void TlsRecvServerHello(Ptr<Socket> socket);

		void StartDns(void);
		void HandleDnsResponse(Ptr<Socket> socket);
		void HandleResourceResponse(Ptr<Socket> socket);

		void SendAndRetry(DnsDotDohRequest request);
		void CancelRetry(DnsDotDohHeader header);
		void ActOnResponse(DnsDotDohHeader response);

		bool m_delayedResponses;

		DnsDotDohProtocol m_protocol;
		Time m_timeout;

		Ptr<Socket> m_recursorSocket;
		Ipv4Address m_recursorAddress;
		uint16_t m_recursorPort;
		uint8_t* m_recursorStream;
		uint32_t m_recursorStreamLength;
		uint32_t m_recursorStreamWriteOffset;
		uint32_t m_recursorStreamReadOffset;

		Ptr<Socket> m_resourceServerSocket;
		Ipv4Address m_resourceServerAddress;
		uint16_t m_resourceServerPort;
		uint8_t* m_resourceServerStream;
		uint32_t m_resourceServerStreamLength;
		uint32_t m_resourceServerStreamWriteOffset;
		uint32_t m_resourceServerStreamReadOffset;

		std::map<uint32_t, std::list<DnsDotDohRequest> > m_requests;
		std::map<uint32_t, EventId> m_requests_retries;
		std::list<DnsDotDohRequest> m_requests_inprogress;
		std::list<DnsDotDohRequest> m_requests_completed;
	};
}

#endif /* DNS_DOT_DOH_CLIENT_H */
/* vim: set noet tw=100 ts=2 sw=2: */
