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

/* Including certificate, sample values from Wireshark WSJ.com */
#define TLS_CLIENT_HELLO (118 + 399 + 1000)
#define TLS_SERVER_HELLO_DONE (83 + 4822 + 831)
#define TLS_CLIENT_DONE (126)

#define TLS_HANDSHAKE_0_DELAY (5)
#define TLS_HANDSHAKE_0_LENGTH (TLS_CLIENT_HELLO)
#define TLS_HANDSHAKE_0_RESPONSE_LENGTH (TLS_SERVER_HELLO_DONE)

#define TLS_HANDSHAKE_1_DELAY (0)
#define TLS_HANDSHAKE_1_LENGTH (TLS_CLIENT_DONE)
#define TLS_HANDSHAKE_1_RESPONSE_LENGTH (0)

#include <map>

#include "ns3/boolean.h"
#include "ns3/enum.h"
#include "ns3/event-id.h"
#include "ns3/inet-socket-address.h"
#include "ns3/ipv4-address.h"
#include "ns3/log.h"
#include "ns3/nstime.h"
#include "ns3/packet.h"
#include "ns3/pointer.h"
#include "ns3/simulator.h"
#include "ns3/socket-factory.h"
#include "ns3/socket.h"
#include "ns3/uinteger.h"

#include "dnsdotdoh-client.h"

namespace ns3 {
	NS_LOG_COMPONENT_DEFINE ("DnsDotDohClientApplication");
	NS_OBJECT_ENSURE_REGISTERED (DnsDotDohClient);

	TypeId DnsDotDohClient::GetTypeId(void) {
		static TypeId tid = TypeId("ns3::DnsDotDohClient")
			.SetParent<Application>()
			.AddConstructor<DnsDotDohClient>()
			.AddAttribute("Protocol",
				"The protocol used for simulation: Do53, DoT, or DoH",
				EnumValue(),
				MakeEnumAccessor(&DnsDotDohClient::m_protocol),
				MakeEnumChecker(DnsDotDohProtocol::Do53, "Do53",
					DnsDotDohProtocol::DoT, "DoT",
					DnsDotDohProtocol::DoH, "DoH"))
			.AddAttribute("RecursorAddress",
				"The recursor's Ipv4Address",
				Ipv4AddressValue(),
				MakeIpv4AddressAccessor(&DnsDotDohClient::m_recursorAddress),
				MakeIpv4AddressChecker())
			.AddAttribute("RecursorPort",
				"The recursor's port",
				UintegerValue(0),
				MakeUintegerAccessor(&DnsDotDohClient::m_recursorPort),
				MakeUintegerChecker<uint16_t>())
			.AddAttribute("ResourceServerAddress",
				"The resource server's Ipv4Address",
				Ipv4AddressValue(),
				MakeIpv4AddressAccessor(&DnsDotDohClient::m_resourceServerAddress),
				MakeIpv4AddressChecker())
			.AddAttribute("ResourceServerPort",
				"The resource server's port",
				UintegerValue(0),
				MakeUintegerAccessor(&DnsDotDohClient::m_resourceServerPort),
				MakeUintegerChecker<uint16_t>())
			.AddAttribute("Timeout",
				"The DNS and HTTP timeout",
				TimeValue(Seconds(10.0)),
				MakeTimeAccessor(&DnsDotDohClient::m_timeout),
				MakeTimeChecker());
		return tid;
	}

	DnsDotDohClient::DnsDotDohClient() {
		NS_LOG_FUNCTION_NOARGS();
		m_delayedResponses = false;

		m_protocol = DnsDotDohProtocol::Do53;
		m_timeout = Seconds(5.0);

		m_recursorSocket = 0;
		m_recursorStreamLength = 1500;
		m_recursorStream = (uint8_t*)std::malloc(m_recursorStreamLength);
		NS_ABORT_IF(nullptr == m_recursorStream);
		m_recursorStreamWriteOffset = 0;
		m_recursorStreamReadOffset = 0;

		m_resourceServerSocket = 0;
		m_resourceServerStreamLength = 1500;
		m_resourceServerStream = (uint8_t*)std::malloc(m_resourceServerStreamLength);
		NS_ABORT_IF(nullptr == m_resourceServerStream);
		m_resourceServerStreamWriteOffset = 0;
		m_resourceServerStreamReadOffset = 0;

		m_requests = std::map<uint32_t, std::list<DnsDotDohRequest> >();
		m_requests_retries = std::map<uint32_t, EventId>();
		m_requests_inprogress = std::list<DnsDotDohRequest>();
		m_requests_completed = std::list<DnsDotDohRequest>();
	}

	void DnsDotDohClient::SetRequests(std::list<DnsDotDohRequest> requests) {
		NS_LOG_FUNCTION_NOARGS();
		for(auto rt = requests.begin(); rt != requests.end(); ++rt) {
			m_requests[rt->m_depends_on].push_front(*rt);
		}
	}

	DnsDotDohClient::~DnsDotDohClient() {
		NS_LOG_FUNCTION_NOARGS();
		std::free(m_recursorStream);
		std::free(m_resourceServerStream);
	}

	void DnsDotDohClient::DoDispose(void) {
		NS_LOG_FUNCTION_NOARGS();
		Application::DoDispose();
	}

	void DnsDotDohClient::StartApplication(void) {
		NS_LOG_FUNCTION_NOARGS();

		TypeId tid;
		switch(m_protocol) {
			case DnsDotDohProtocol::Do53:
				tid = TypeId::LookupByName("ns3::UdpSocketFactory");
				break;
			case DnsDotDohProtocol::DoT:
			case DnsDotDohProtocol::DoH:
				tid = TypeId::LookupByName("ns3::TcpSocketFactory");
				break;
		}

		if(!m_recursorSocket) {
			m_recursorSocket = Socket::CreateSocket(GetNode(), tid);

			if(m_protocol == DnsDotDohProtocol::DoT || m_protocol == DnsDotDohProtocol::DoH) {
				m_recursorSocket->SetAttribute("TcpNoDelay", BooleanValue(true));
				m_recursorSocket->SetAttribute("SegmentSize", UintegerValue(1460));
			}

			m_recursorSocket->Bind();
			m_recursorSocket->Connect(InetSocketAddress(m_recursorAddress, m_recursorPort));
		}

		if(!m_resourceServerSocket) {
			m_resourceServerSocket = Socket::CreateSocket(GetNode(), TypeId::LookupByName("ns3::TcpSocketFactory"));
			m_resourceServerSocket->SetAttribute("TcpNoDelay", BooleanValue(true));
			m_resourceServerSocket->SetAttribute("SegmentSize", UintegerValue(1460));
			m_resourceServerSocket->Bind();
			m_resourceServerSocket->SetRecvCallback(MakeCallback(&DnsDotDohClient::HandleResourceResponse, this));
			m_resourceServerSocket->Connect(InetSocketAddress(m_resourceServerAddress, m_resourceServerPort));
		}

		NS_LOG_INFO("Recursor: " << m_recursorAddress << ":" << m_recursorPort);
		NS_LOG_INFO("Resource Server: " << m_resourceServerAddress << ":" << m_resourceServerPort);

		Send();
	}

	void DnsDotDohClient::StopApplication() {
		NS_LOG_FUNCTION_NOARGS();

		if(0 != m_recursorSocket) {
			NS_ABORT_IF(0 != m_recursorSocket->Close());
			m_recursorSocket->SetRecvCallback(MakeNullCallback<void, Ptr<Socket> >());
			m_recursorSocket = 0;
		}

		if(0 != m_resourceServerSocket) {
			NS_ABORT_IF(0 != m_resourceServerSocket->Close());
			m_resourceServerSocket->SetRecvCallback(MakeNullCallback<void, Ptr<Socket> >());
			m_resourceServerSocket = 0;
		}
	}

	/* Simulate TLS Handshake */
	void DnsDotDohClient::TlsSendClientHello(void) {
		NS_LOG_FUNCTION_NOARGS();

		auto r = DnsDotDohHeader(0, TLS_HANDSHAKE_0_RESPONSE_LENGTH, TLS_HANDSHAKE_0_DELAY,
				TLS_HANDSHAKE_0_LENGTH - DnsDotDohHeader::Length());
		Ptr<Packet> p = Create<Packet>(r.WireFormat(), r.WireFormatLength());

		m_recursorSocket->SetRecvCallback(MakeCallback(&DnsDotDohClient::TlsRecvServerHello, this));
		m_recursorSocket->Send(p);
	}

	void DnsDotDohClient::TlsRecvServerHello(Ptr<Socket> socket) {
		NS_LOG_FUNCTION_NOARGS();

		/* Append data */
		for(uint32_t read_ = 1; read_ != 0; m_recursorStreamWriteOffset += read_) {
			read_ = socket->Recv(m_recursorStream + m_recursorStreamWriteOffset,
					m_recursorStreamLength - m_recursorStreamWriteOffset, 0);
			if(read_ == m_recursorStreamLength - m_recursorStreamWriteOffset) {
				/* We read the maximum allowed, buffer is full, resize */
				uint32_t streamNewLength = m_recursorStreamLength + 1500;
				m_recursorStream = (uint8_t*)std::realloc(m_recursorStream, streamNewLength);
				NS_ABORT_IF(nullptr == m_recursorStream);
			}
		}

		/* Consume until no data, one header at most, still in TLS handshake */
		if(m_recursorStreamReadOffset + DnsDotDohHeader::Length() < m_recursorStreamWriteOffset) {
			auto header = DnsDotDohHeader::Parse(m_recursorStream + m_recursorStreamReadOffset);
			if(m_recursorStreamReadOffset + DnsDotDohHeader::Length() + header.m_pad_to_next
					<= m_recursorStreamWriteOffset) {
				/* "Consume" data */
				m_recursorStreamReadOffset += DnsDotDohHeader::Length() + header.m_pad_to_next;

				auto r = DnsDotDohHeader(0, TLS_HANDSHAKE_1_RESPONSE_LENGTH, TLS_HANDSHAKE_1_DELAY,
						TLS_HANDSHAKE_1_LENGTH - DnsDotDohHeader::Length());
				Ptr<Packet> p = Create<Packet>(r.WireFormat(), r.WireFormatLength());

				m_recursorSocket->SetRecvCallback(MakeCallback(&DnsDotDohClient::HandleDnsResponse, this));
				m_recursorSocket->Send(p);
				StartDns();
			}
		}

		/* Move stream window forward */
		m_recursorStreamWriteOffset -= m_recursorStreamReadOffset; /* Amount of data not consumed */
		uint32_t streamNewLength = m_recursorStreamWriteOffset + 1500;
		uint8_t* streamNew = (uint8_t*)std::malloc(streamNewLength);
		NS_ABORT_IF(nullptr == streamNew);

		std::memcpy(streamNew, m_recursorStream + m_recursorStreamReadOffset, streamNewLength);
		std::free(m_recursorStream);

		m_recursorStream = streamNew;
		m_recursorStreamLength = streamNewLength;
		m_recursorStreamReadOffset = 0;
	}

	/* General Simulation */
	void DnsDotDohClient::Send(void) {
		NS_LOG_FUNCTION_NOARGS();
		if(m_protocol == DoT || m_protocol == DoH) {
			TlsSendClientHello();
		} else {
			m_recursorSocket->SetRecvCallback(MakeCallback(&DnsDotDohClient::HandleDnsResponse, this));
			StartDns();
		}
	}

	void DnsDotDohClient::StartDns(void) {
		NS_LOG_FUNCTION_NOARGS();
		ActOnResponse(DnsDotDohHeader(0, 0, 0, 0));
	}

	void DnsDotDohClient::HandleDnsResponse(Ptr<Socket> socket) {
		NS_LOG_FUNCTION_NOARGS();

		/* Append data */
		for(uint32_t read_ = 1; read_ != 0; m_recursorStreamWriteOffset += read_) {
			read_ = socket->Recv(m_recursorStream + m_recursorStreamWriteOffset,
					m_recursorStreamLength - m_recursorStreamWriteOffset, 0);
			if(read_ == m_recursorStreamLength - m_recursorStreamWriteOffset) {
				/* We read the maximum allowed, buffer is full, resize */
				uint32_t streamNewLength = m_recursorStreamLength + 1500;
				m_recursorStream = (uint8_t*)std::realloc(m_recursorStream, streamNewLength);
				NS_ABORT_IF(nullptr == m_recursorStream);
			}
		}

		/* Consume until we are missing data */
		while(m_recursorStreamReadOffset + DnsDotDohHeader::Length() < m_recursorStreamWriteOffset) {
			auto header = DnsDotDohHeader::Parse(m_recursorStream + m_recursorStreamReadOffset);
			if(m_recursorStreamReadOffset + DnsDotDohHeader::Length() + header.m_pad_to_next
					<= m_recursorStreamWriteOffset) {
				/* "Consume" data */
				m_recursorStreamReadOffset += DnsDotDohHeader::Length() + header.m_pad_to_next;
				ActOnResponse(header);
			} else {
				break; /* We are missing data, exit loop */
			}
		}

		/* Move stream window forward */
		m_recursorStreamWriteOffset -= m_recursorStreamReadOffset; /* Amount of data not consumed */
		uint32_t streamNewLength = m_recursorStreamWriteOffset + 1500;
		uint8_t* streamNew = (uint8_t*)std::malloc(streamNewLength);
		NS_ABORT_IF(nullptr == streamNew);

		std::memcpy(streamNew, m_recursorStream + m_recursorStreamReadOffset, streamNewLength);
		std::free(m_recursorStream);

		m_recursorStream = streamNew;
		m_recursorStreamLength = streamNewLength;
		m_recursorStreamReadOffset = 0;
	}

	void DnsDotDohClient::HandleResourceResponse(Ptr<Socket> socket) {
		NS_LOG_FUNCTION_NOARGS();

		/* Append data */
		for(uint32_t read_ = 1; read_ != 0; m_resourceServerStreamWriteOffset += read_) {
			read_ = socket->Recv(m_resourceServerStream + m_resourceServerStreamWriteOffset,
					m_resourceServerStreamLength - m_resourceServerStreamWriteOffset, 0);
			if(read_ == m_resourceServerStreamLength - m_resourceServerStreamWriteOffset) {
				/* We read the maximum allowed, buffer is full, resize */
				uint32_t streamNewLength = m_resourceServerStreamLength + 1500;
				m_resourceServerStream = (uint8_t*)std::realloc(m_resourceServerStream, streamNewLength);
				NS_ABORT_IF(nullptr == m_resourceServerStream);
			}
		}

		/* Consume until we are missing data */
		while(m_resourceServerStreamReadOffset + DnsDotDohHeader::Length() < m_resourceServerStreamWriteOffset) {
			auto header = DnsDotDohHeader::Parse(m_resourceServerStream + m_resourceServerStreamReadOffset);
			CancelRetry(header);
			if(m_resourceServerStreamReadOffset + DnsDotDohHeader::Length() + header.m_pad_to_next
					<= m_resourceServerStreamWriteOffset) {
				/* "Consume" data */
				m_resourceServerStreamReadOffset += DnsDotDohHeader::Length() + header.m_pad_to_next;
				ActOnResponse(header);
			} else {
				NS_LOG_INFO("Transfer not yet completed, but attempting to cancel retry " << header.m_id);
				NS_LOG_INFO(m_resourceServerStreamReadOffset << " vs. " << m_resourceServerStreamWriteOffset);
				break; /* We are missing data, exit loop */
			}
		}

		/* Move stream window forward */
		m_resourceServerStreamWriteOffset -= m_resourceServerStreamReadOffset; /* Not consumed */
		uint32_t streamNewLength = m_resourceServerStreamWriteOffset + 1500;
		uint8_t* streamNew = (uint8_t*)std::malloc(streamNewLength);
		NS_ABORT_IF(nullptr == streamNew);

		std::memcpy(streamNew, m_resourceServerStream + m_resourceServerStreamReadOffset, m_resourceServerStreamWriteOffset);
		std::free(m_resourceServerStream);

		m_resourceServerStream = streamNew;
		m_resourceServerStreamLength = streamNewLength;
		m_resourceServerStreamReadOffset = 0;
	}

	void DnsDotDohClient::CancelRetry(DnsDotDohHeader header) {
		NS_LOG_FUNCTION(header.m_id);
		auto event = m_requests_retries.find(header.m_id);
		if(m_requests_retries.end() != event) {
			Simulator::Remove(event->second);
			NS_LOG_INFO("Cancelled retry event " << event->first);
			m_requests_retries.erase(event);
			NS_LOG_INFO("Retries left: " << m_requests_retries.size());
		}
	}

	void DnsDotDohClient::ActOnResponse(DnsDotDohHeader response) {
		NS_LOG_FUNCTION(response.m_id);

		/* On First Response: Copy my ID from inprogress to completed */
		for(auto it = m_requests_inprogress.begin(); it != m_requests_inprogress.end(); ++it) {
			if(it->m_id == response.m_id) {
				NS_LOG_INFO("Completed request " << response.m_id);
				CancelRetry(response);
				m_requests_completed.push_back(*it);
				m_requests_inprogress.erase(it);
				break;
			}
		}
		NS_LOG_INFO("Acting on " << response.m_id << " -> " << Simulator::Now().As(Time::S));

		/* Resolve dependencies */
		auto reqt = m_requests.find(response.m_id);
		if(m_requests.end() != reqt) {
			NS_LOG_INFO("Resolving requests depending on " << reqt->first);
			for(auto rt = reqt->second.begin(); rt != reqt->second.end(); ++rt) {
				Simulator::ScheduleNow(&DnsDotDohClient::SendAndRetry, this, *rt);
				m_requests_inprogress.push_back(*rt);
			}
			m_requests.erase(response.m_id);
		}

		if(m_requests_inprogress.empty() && !m_delayedResponses) {
			std::cout << Simulator::Now().As(Time::S) << std::endl;
			/* Depending on link settings, we might receive delayed responses, we ignore them for
			** our timeout calculation */
			m_delayedResponses = true;
		}
	}

	void DnsDotDohClient::SendAndRetry(DnsDotDohRequest r) {
		auto rr = DnsDotDohHeader(r.m_id, r.m_response_length, r.m_delay,
				r.m_request_length - DnsDotDohHeader::Length());
		Ptr<Packet> p;
		switch(r.m_type) {
			case DnsDotDohRequestType::DNS:
				rr.m_pad_to_next += 0;	/* TODO: Do53 Overhead */
				p = Create<Packet>(rr.WireFormat(), rr.WireFormatLength());
				m_recursorSocket->Send(p);
				NS_LOG_INFO("Sent DNS request\t" << rr);
				break;
			case DnsDotDohRequestType::HTTP:
				rr.m_pad_to_next += 0; /* TODO: DoT and DoH Overhead */
				p = Create<Packet>(rr.WireFormat(), rr.WireFormatLength());
				m_resourceServerSocket->Send(p);
				NS_LOG_INFO("Sent HTTP request\t" << rr);
				break;
		}

		auto event = Simulator::Schedule(m_timeout, &DnsDotDohClient::SendAndRetry, this, r);
		m_requests_retries[r.m_id] = event;
	}
}
/* vim: set noet tw=100 ts=2 sw=2: */
