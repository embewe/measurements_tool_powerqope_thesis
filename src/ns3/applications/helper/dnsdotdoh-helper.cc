/*
 * Copyright (c) 2019 Princeton University
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA	02111-1307	USA
 *
 * Author: Kevin Borgolte <borgolte@cs.princeton.edu>
 *				 Paul Schmitt <pschmitt@cs.princeton.edu>
 */

#include "ns3/enum.h"
#include "ns3/ipv4-address.h"
#include "ns3/nstime.h"
#include "ns3/uinteger.h"

#include "ns3/dnsdotdoh-client.h"
#include "ns3/dnsdotdoh-server.h"

#include "dnsdotdoh-helper.h"

namespace ns3 {
	DnsDotDohServerHelper::DnsDotDohServerHelper(Ipv4Address address, uint16_t port) {
		m_factory.SetTypeId(DnsDotDohServer::GetTypeId());
		SetAttribute("Address", Ipv4AddressValue(address));
		SetAttribute("Port", UintegerValue(port));
	}

	void DnsDotDohServerHelper::SetAttribute(std::string name, const AttributeValue &value) {
		m_factory.Set(name, value);
	}

	ApplicationContainer DnsDotDohServerHelper::Install(Ptr<Node> node) const {
		Ptr<Application> app = m_factory.Create<DnsDotDohServer>();
		node->AddApplication(app);
		return ApplicationContainer(app);
	}

	DnsDotDohClientHelper::DnsDotDohClientHelper(Ipv4Address recursorAddress,
					uint16_t recursorPort, DnsDotDohProtocol protocol,
					Ipv4Address resourceAddress, uint16_t resourcePort, Time timeout) {
		m_factory.SetTypeId(DnsDotDohClient::GetTypeId());
		SetAttribute("RecursorAddress", Ipv4AddressValue(recursorAddress));
		SetAttribute("RecursorPort", UintegerValue(recursorPort));
		SetAttribute("Protocol", EnumValue(protocol));
		SetAttribute("ResourceServerAddress", Ipv4AddressValue(resourceAddress));
		SetAttribute("ResourceServerPort", UintegerValue(resourcePort));
		SetAttribute("Timeout", TimeValue(timeout));
	}

	void DnsDotDohClientHelper::SetAttribute(std::string name, const AttributeValue &value) {
		m_factory.Set(name, value);
	}

	ApplicationContainer DnsDotDohClientHelper::Install(Ptr<Node> node,
			std::list<DnsDotDohRequest> requests) const {
		Ptr<DnsDotDohClient> client = m_factory.Create<DnsDotDohClient>();
		client->SetRequests(requests);
		Ptr<Application> app = client;
		node->AddApplication(app);
		return ApplicationContainer(app);
	}
}
/* vim: set noet tw=100 ts=2 sw=2: */
