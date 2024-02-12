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

#include <iostream>
#include <list>

#include "ns3/log.h"
#include "ns3/socket.h"
#include "ns3/packet.h"
#include "ns3/header.h"
#include "ns3/ipv4-header.h"

#include "dnsdotdoh-common.h"

namespace ns3 {
  NS_LOG_COMPONENT_DEFINE ("DnsDotDohCommon");

	std::ostream& operator<< (std::ostream &os, const DnsDotDohProtocol& protocol) {
		switch(protocol) {
			case DnsDotDohProtocol::Do53:
				os << "Plain DNS (Do53)";
				break;
			case DnsDotDohProtocol::DoT:
				os << "DNS over TLS (DoT)";
				break;
			case DnsDotDohProtocol::DoH:
				os << "DNS over HTTP (DoH)";
				break;
		}
		return os;
	};

	std::istream& operator>> (std::istream &is, DnsDotDohProtocol& protocol) {
		if('d' == tolower(is.peek())) {
			is.seekg(1, std::ios_base::cur);
			if('o' == tolower(is.peek())) {
				is.seekg(1, std::ios_base::cur);
				int c = is.peek();
				if('5' == c) {
					is.seekg(1, std::ios_base::cur);
					if('3' == is.peek()) {
						is.seekg(1, std::ios_base::cur);
						protocol = DnsDotDohProtocol::Do53;
						return is;
					}
				} else if ('t' == tolower(c)) {
					is.seekg(1, std::ios_base::cur);
					protocol = DnsDotDohProtocol::DoT;
					return is;
				} else if ('h' == tolower(c)) {
					is.seekg(1, std::ios_base::cur);
					protocol = DnsDotDohProtocol::DoH;
					return is;
				}
				/* fail */
			}
			/* fail */
		}
		return is;
	};
	std::ostream& operator<< (std::ostream &os, const DnsDotDohRequestType& rt) {
		switch(rt) {
			case DnsDotDohRequestType::DNS:
				os << "DNS";
				break;
			case DnsDotDohRequestType::HTTP:
				os << "HTTP";
				break;
		}
		return os;
	};

	DnsDotDohRequest::DnsDotDohRequest(uint32_t id, uint32_t depends_on, DnsDotDohRequestType type,
			float delay, uint32_t request_length, uint32_t response_length) {
		m_id = id;
		m_depends_on = depends_on;
		m_type = type;
		m_delay = delay;
		m_request_length = request_length;
		m_response_length = response_length;
	}

	std::ostream& operator<< (std::ostream&os, const DnsDotDohRequest& r) {
		os << "DnsDotDohRequest<" <<
			"id=" << r.m_id << " " <<
			"depends_on=" << r.m_depends_on << " " <<
			"type=" << r.m_type << " " <<
			"delay=" << r.m_delay << " " <<
			"request_length=" << r.m_request_length << " "
			"response_length=" << r.m_response_length << ">";
		return os;
	}

	DnsDotDohHeader::DnsDotDohHeader() {};

	DnsDotDohHeader::DnsDotDohHeader(uint16_t id, uint32_t response_length, float delay,
			uint32_t pad_to_next) {
		m_id = id;
		m_response_length = response_length;
		m_delay = delay;
		m_pad_to_next = pad_to_next;
	}

	DnsDotDohHeader DnsDotDohHeader::Parse(uint8_t buffer[]) {
		DnsDotDohHeader rr;

		size_t offset = 0;
		memcpy(&rr.m_id, buffer + offset, sizeof(rr.m_id)/sizeof(uint8_t));
		offset += sizeof(rr.m_id);

		memcpy(&rr.m_response_length, buffer + offset, sizeof(rr.m_response_length)/sizeof(uint8_t));
		offset += sizeof(rr.m_response_length);

		memcpy(&rr.m_delay, buffer + offset, sizeof(rr.m_delay)/sizeof(uint8_t));
		offset += sizeof(rr.m_delay);

		memcpy(&rr.m_pad_to_next, buffer + offset, sizeof(rr.m_pad_to_next)/sizeof(uint8_t));
		offset += sizeof(rr.m_pad_to_next);

		return rr;
	}

	size_t DnsDotDohHeader::Length() {
		return sizeof(m_id) + sizeof(m_response_length) +
			sizeof(m_delay) + sizeof(m_pad_to_next);
	}

	const uint8_t* DnsDotDohHeader::WireFormat(void) {
		uint8_t *m__raw = new uint8_t[WireFormatLength()];

		size_t offset = 0, length = sizeof(m_id) / sizeof(uint8_t);
		memcpy(m__raw + offset, &m_id, length);
		offset += length;

		length = sizeof(m_response_length) / sizeof(uint8_t);
		memcpy(m__raw + offset, &m_response_length, length);
		offset += length;

		length = sizeof(m_delay) / sizeof(uint8_t);
		memcpy(m__raw + offset, &m_delay, length);
		offset += length;

		length = sizeof(m_pad_to_next) / sizeof(uint8_t);
		memcpy(m__raw + offset, &m_pad_to_next, length);
		offset += length;

		length = m_pad_to_next;
		bzero(m__raw + offset, m_pad_to_next);

		return m__raw;
	}

	size_t DnsDotDohHeader::WireFormatLength(void) {
		return Length() + m_pad_to_next;
	}

	std::ostream& operator<< (std::ostream&os, const DnsDotDohHeader& rr) {
		os << "DnsDotDohHeader<" <<
			"id=" << rr.m_id << " " <<
			"response_length=" << rr.m_response_length << " " <<
			"delay=" << rr.m_delay << " " <<
			"pad_to_next=" << rr.m_pad_to_next << ">";
		return os;
	}
}
/* vim: set noet tw=100 ts=2 sw=2: */
