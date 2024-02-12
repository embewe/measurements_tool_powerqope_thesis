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

#include "ns3/log.h"
#include "ns3/abort.h"
#include "ns3/ipv4-address.h"
#include "ns3/address-utils.h"
#include "ns3/boolean.h"
#include "ns3/nstime.h"
#include "ns3/inet-socket-address.h"
#include "ns3/socket.h"
#include "ns3/tcp-socket.h"
#include "ns3/simulator.h"
#include "ns3/socket-factory.h"
#include "ns3/packet.h"
#include "ns3/uinteger.h"

#include "dnsdotdoh-common.h"
#include "dnsdotdoh-server.h"

namespace ns3 {
	NS_LOG_COMPONENT_DEFINE ("DnsDotDohServerApplication");
	NS_OBJECT_ENSURE_REGISTERED (DnsDotDohServer);

	TypeId DnsDotDohServer::GetTypeId(void) {
		static TypeId tid = TypeId("ns3::DnsDotDohServer")
			.SetParent<Application>()
			.AddConstructor<DnsDotDohServer>()
			.AddAttribute("Address", "The Address on which to Bind the rx socket.",
				Ipv4AddressValue(),
				MakeIpv4AddressAccessor(&DnsDotDohServer::m_address),
				MakeIpv4AddressChecker())
			.AddAttribute("Port", "Port on which we listen for incoming packets.",
				UintegerValue(9),
				MakeUintegerAccessor (&DnsDotDohServer::m_port),
				MakeUintegerChecker<uint16_t>());
		return tid;
	}

	DnsDotDohServer::DnsDotDohServer() {
		NS_LOG_FUNCTION_NOARGS();
		m_streamLength = 1500;
		m_stream = (uint8_t*)std::malloc(m_streamLength);
		NS_ABORT_IF(nullptr == m_stream);
		m_streamWriteOffset = 0;
		m_streamReadOffset = 0;
		m_tcpSocket = 0;
		m_udpSocket = 0;
	}

	DnsDotDohServer::~DnsDotDohServer() {
		NS_LOG_FUNCTION_NOARGS ();
		m_tcpSocket = 0;
		m_udpSocket = 0;
	}

	void DnsDotDohServer::DoDispose(void) {
		NS_LOG_FUNCTION_NOARGS();
		Application::DoDispose();
	}

	void DnsDotDohServer::StartApplication(void) {
		NS_LOG_FUNCTION_NOARGS();
		InetSocketAddress local = InetSocketAddress(m_address, m_port);

		if(0 == m_tcpSocket) {
			m_tcpSocket = Socket::CreateSocket(GetNode(), TypeId::LookupByName("ns3::TcpSocketFactory"));
			m_tcpSocket->SetAttribute("TcpNoDelay", BooleanValue(true));
			m_tcpSocket->SetAttribute("SegmentSize", UintegerValue(1460));
			NS_ABORT_IF(0 != m_tcpSocket->Bind(local));
			m_tcpSocket->Listen();
			m_tcpSocket->SetRecvCallback(MakeCallback(&DnsDotDohServer::HandleTcpRead, this));
			m_tcpSocket->SetAcceptCallback(MakeNullCallback<bool, Ptr<Socket>, const Address &>(),
				MakeCallback(&DnsDotDohServer::HandleTcpAccept, this));
			m_tcpSocket->SetCloseCallbacks(MakeCallback(&DnsDotDohServer::HandleTcpClose, this),
				MakeCallback(&DnsDotDohServer::HandleTcpClose, this));
		}

		if(0 == m_udpSocket) {
			m_udpSocket = Socket::CreateSocket(GetNode(), TypeId::LookupByName("ns3::UdpSocketFactory"));
			NS_ABORT_IF(0 != m_udpSocket->Bind(local));
			m_udpSocket->Listen();
			m_udpSocket->SetRecvCallback(MakeCallback(&DnsDotDohServer::HandleUdpRead, this));
		}

		NS_LOG_INFO("Listening on: " << m_address << " port: " << m_port << " TCP and UDP");
	}

	void DnsDotDohServer::HandleTcpClose(Ptr<Socket> socket) {
		NS_LOG_FUNCTION_NOARGS();
		socket->Close();
	}

	void DnsDotDohServer::HandleTcpAccept(Ptr<Socket> socket, const Address& from) {
		NS_LOG_FUNCTION_NOARGS();
		socket->SetRecvCallback(MakeCallback(&DnsDotDohServer::HandleTcpRead, this));
	}

	void DnsDotDohServer::StopApplication() {
		NS_LOG_FUNCTION_NOARGS();
		if(m_tcpSocket != 0) {
			m_tcpSocket->Close();
			m_tcpSocket->SetRecvCallback(MakeNullCallback<void, Ptr<Socket> >());
			m_tcpSocket->SetAcceptCallback(MakeNullCallback<bool, Ptr<Socket>, const Address &>(),
				MakeNullCallback<void, Ptr<Socket>, const Address &>());
			m_tcpSocket->SetCloseCallbacks(MakeNullCallback<void, Ptr<Socket> >(),
				MakeNullCallback<void, Ptr<Socket> >());
			m_tcpSocket = 0;
		}

		if(m_udpSocket != 0) {
			m_udpSocket->Close();
			m_udpSocket->SetRecvCallback(MakeNullCallback<void, Ptr<Socket> >());
			m_udpSocket = 0;
		}
	}

	void DnsDotDohServer::HandleTcpRead(Ptr<Socket> socket) {
		NS_LOG_FUNCTION_NOARGS();

		/* Append data */
		for(uint32_t read_ = 1; read_ != 0; m_streamWriteOffset += read_) {
			read_ = socket->Recv(m_stream + m_streamWriteOffset,
					m_streamLength - m_streamWriteOffset, 0);
			if(read_ == m_streamLength - m_streamWriteOffset) {
				/* We read the maximum allowed, buffer is full, resize */
				uint32_t streamNewLength = m_streamLength + 1500;
				m_stream = (uint8_t*)std::realloc(m_stream, streamNewLength);
				NS_ABORT_IF(nullptr == m_stream);
			}
		}

		/* Consume until we are missing data */
		while(m_streamReadOffset + DnsDotDohHeader::Length() < m_streamWriteOffset) {
			auto header = DnsDotDohHeader::Parse(m_stream + m_streamReadOffset);
			if(m_streamReadOffset + DnsDotDohHeader::Length() + header.m_pad_to_next
					<= m_streamWriteOffset) {
				m_streamReadOffset += DnsDotDohHeader::Length() + header.m_pad_to_next; /* "Consume" data */
				if(header.m_response_length > DnsDotDohHeader::Length()) {
					/* Only respond if we need to send more than Header::Length() bytes */
					header.m_pad_to_next = header.m_response_length - DnsDotDohHeader::Length();
					header.m_response_length = 0;

					NS_LOG_INFO("Scheduling response in " << header.m_delay << " seconds " << header);
					Ptr<Packet> pkt = Create<Packet>(header.WireFormat(), header.WireFormatLength());
					Simulator::Schedule(Seconds(header.m_delay), &DnsDotDohServer::SendTcp, this, socket, pkt);
				}
			} else {
				break;
			}
		}

		/* Move stream window forward */
		m_streamWriteOffset -= m_streamReadOffset; /* Amount of data not consumed */
		uint32_t streamNewLength = m_streamWriteOffset + 1500;
		uint8_t* streamNew = (uint8_t*)std::malloc(streamNewLength);
		NS_ABORT_IF(nullptr == streamNew);

		std::memcpy(streamNew, m_stream + m_streamReadOffset, m_streamWriteOffset);
		std::free(m_stream);

		m_stream = streamNew;
		m_streamLength = streamNewLength;
		m_streamReadOffset = 0;
	}

	void DnsDotDohServer::HandleUdpRead(Ptr<Socket> socket) {
		NS_LOG_FUNCTION_NOARGS();
		Address address;
		Ptr<Packet> packet = socket->RecvFrom(address);

		if(packet->GetSize() > DnsDotDohHeader::Length()) {
			m_streamLength = packet->GetSize();
			m_stream = (uint8_t*)std::realloc(m_stream, m_streamLength);
			packet->CopyData(m_stream, m_streamLength);

			m_streamReadOffset = 0;

			/* Consume until we are missing data */
			while(m_streamReadOffset + DnsDotDohHeader::Length() < m_streamLength) {
				auto header = DnsDotDohHeader::Parse(m_stream + m_streamReadOffset);
				if(m_streamReadOffset + DnsDotDohHeader::Length() + header.m_pad_to_next <= m_streamLength) {
					m_streamReadOffset += DnsDotDohHeader::Length() + header.m_pad_to_next; /* "Consume" data */
					if(header.m_response_length > DnsDotDohHeader::Length()) {
						/* Only respond if we need to send more than Header::Length bytes */
						header.m_pad_to_next = header.m_response_length - DnsDotDohHeader::Length();
						header.m_response_length = 0;

						NS_LOG_INFO("Scheduling response in " << header.m_delay << " seconds " << header);
						Ptr<Packet> pkt = Create<Packet>(header.WireFormat(), header.WireFormatLength());
						Simulator::Schedule(Seconds(header.m_delay), &DnsDotDohServer::SendToUdp, this, address, pkt);
					}
				}
			}
			NS_ABORT_IF(m_streamReadOffset != m_streamLength);
		}
	}

	/* TODO: Should we respond to ids that have been already responded to, but which may be queued?
	** We currently log the time when the client receives the first response.
	**/

	void DnsDotDohServer::SendTcp(Ptr<Socket> socket, Ptr<Packet> packet) {
		NS_LOG_FUNCTION_NOARGS();
		NS_LOG_INFO("Sending packet of size " << packet->GetSize());
		socket->Send(packet);
	}

	void DnsDotDohServer::SendToUdp(Address address, Ptr<Packet> packet) {
		NS_LOG_FUNCTION_NOARGS();
		NS_LOG_INFO("Sending packet of size " << packet->GetSize() << " to " << address);
		m_udpSocket->SendTo(packet, 0, address);
	}
}
/* vim: set noet tw=100 ts=2 sw=2: */
