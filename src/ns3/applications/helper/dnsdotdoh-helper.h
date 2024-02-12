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

#ifndef DNS_DOT_DOH_HELPER_H
#define DNS_DOT_DOH_HELPER_H

#include "ns3/application-container.h"
#include "ns3/object-factory.h"
#include "ns3/pointer.h"

#include "ns3/dnsdotdoh-common.h"

namespace ns3 {
	class Ipv4Address;
	class Node;
	class Time;

  class DnsDotDohServerHelper {
    public:
      DnsDotDohServerHelper(Ipv4Address address, uint16_t port);

      void SetAttribute(std::string name, const AttributeValue &value);
      ApplicationContainer Install(Ptr<Node> node) const;

    private:
      ObjectFactory m_factory;
  };

  class DnsDotDohClientHelper {
    public:
			DnsDotDohClientHelper(Ipv4Address recursorAddress, uint16_t recursorPort,
				DnsDotDohProtocol protocol, Ipv4Address resourceAddress, uint16_t resourcePort,
				Time timeout);

      void SetAttribute(std::string name, const AttributeValue &value);
      ApplicationContainer Install(Ptr<Node> node, std::list<DnsDotDohRequest> requests) const;

    private:
      ObjectFactory m_factory;
  };
}
#endif /* DNS_DOT_DOH_HELPER_H */
/* vim: set noet tw=100 ts=2 sw=2: */
