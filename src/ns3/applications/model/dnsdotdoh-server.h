/*
 * Copyright (c) 2019 Princeton University
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Author: Kevin Borgolte <borgolte@cs.princeton.edu>
 *         Paul Schmitt <pschmitt@cs.princeton.edu>
 */

#ifndef DNS_DOT_DOH_SERVER_H
#define DNS_DOT_DOH_SERVER_H

#include <map>

#include "ns3/application.h"
#include "ns3/event-id.h"
#include "ns3/ptr.h"
#include "ns3/ipv4-address.h"
#include "ns3/inet-socket-address.h"

namespace ns3 {
	class Socket;
	class Packet;

	class DnsDotDohServer : public Application {
		public:
			static TypeId GetTypeId (void);
			DnsDotDohServer ();
			virtual ~DnsDotDohServer ();

		protected:
			virtual void DoDispose (void);

		private:
			virtual void StartApplication (void);
			virtual void StopApplication (void);

			void HandleTcpRead (Ptr<Socket> socket);
			void HandleUdpRead (Ptr<Socket> socket);
			void HandleTcpAccept (Ptr<Socket> socket, const Address& from);
			void HandleTcpClose (Ptr<Socket> socket);
			void SendTcp(Ptr<Socket> socket, Ptr<Packet> packet);
			void SendToUdp(Address address, Ptr<Packet> packet);

			Ipv4Address m_address;
			uint16_t m_port;

			Ptr<Socket> m_tcpSocket;
			Ptr<Socket> m_udpSocket;

			uint8_t* m_stream;
			uint32_t m_streamLength;
			uint32_t m_streamWriteOffset;
			uint32_t m_streamReadOffset;
	};
}
#endif
/* vim: set noet tw=100 ts=2 sw=2: */
