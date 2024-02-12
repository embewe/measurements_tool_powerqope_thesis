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

#ifndef DNS_DOT_DOH_COMMON_H
#define DNS_DOT_DOH_COMMON_H

#include <iostream>
#include <list>

#include "ns3/pointer.h"

namespace ns3 {
	class Packet;
	class Socket;

	enum DnsDotDohProtocol {
		Do53 = 1,
		DoT = 2,
		DoH = 3,
	};

	std::ostream& operator<< (std::ostream& os, const DnsDotDohProtocol& protocol);
	std::istream& operator>> (std::istream& is, DnsDotDohProtocol& protocol);

	enum DnsDotDohRequestType {
		DNS = 1,
		HTTP = 2,
	};

	class DnsDotDohRequest {
		public:
			uint32_t m_id;
			uint32_t m_depends_on;
			DnsDotDohRequestType m_type;
			float m_delay;
			uint32_t m_request_length;
			uint32_t m_response_length;

			DnsDotDohRequest(uint32_t id, uint32_t depends_on, DnsDotDohRequestType type, float delay,
					uint32_t request_length, uint32_t response_length);
	};

	std::ostream& operator<< (std::ostream& os, const DnsDotDohRequest& r);

	class DnsDotDohHeader {
	public:
		uint16_t m_id;
		uint32_t m_response_length;
		float m_delay;
		uint32_t m_pad_to_next;

		DnsDotDohHeader();
		DnsDotDohHeader(uint16_t id, uint32_t response_length, float delay, uint32_t pad_to_next);

		const uint8_t* WireFormat();
		size_t WireFormatLength();

		static DnsDotDohHeader Parse(uint8_t buffer[]);
		static size_t Length();
  };

	std::ostream& operator<< (std::ostream& os, const DnsDotDohHeader& r);
}
#endif // DNS_DOT_DOH_COMMON_H
/* vim: set noet tw=100 ts=2 sw=2: */
