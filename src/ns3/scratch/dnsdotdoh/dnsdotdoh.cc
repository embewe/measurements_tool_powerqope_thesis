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

#ifndef DEBUG
#define DEBUG (1)
#endif

#ifndef PCAP
#define PCAP (0)
#endif

#include <algorithm>
#include <fstream>
#include <string>

#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/pointer.h"

#include "ns3/dnsdotdoh-common.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("DnsDotDoh");

int main(int argc, char *argv[]) {
#if DEBUG
	LogComponentEnable("Node", LOG_INFO);
	LogComponentEnable("DnsDotDohServerApplication", LOG_FUNCTION);
	LogComponentEnable("DnsDotDohClientApplication", LOG_FUNCTION);
	LogComponentEnable("DnsDotDohClientApplication", LOG_INFO);
	LogComponentEnable("DnsDotDohCommon", LOG_INFO);
	LogComponentEnable("DnsDotDoh", LOG_INFO);
#endif

	std::string requests_filename = "example.rqst";
	std::string datarate = "10Mbps";
	std::string latency = "0ms";
	double loss = 0.0;
	DnsDotDohProtocol protocol = DnsDotDohProtocol::Do53;
	Time duration = Seconds(600.0), timeout = Seconds(15);

	CommandLine cmd;
	cmd.AddValue("datarate", "Data rate to the Internet (Mbps)", datarate);
	cmd.AddValue("latency", "Additional latency (ms)", latency);
	cmd.AddValue("loss", "Loss (0 to 1)", loss);
	cmd.AddValue("protocol", "Protocol { Do53 | DoT | DoH }", protocol);
	cmd.AddValue("timeout", "Timeout for DNS/HTTP requests (s)", timeout);
	cmd.AddValue("duration", "Maximum simulated duration (s)", duration);
	cmd.AddValue("requests", "Filename of requests", requests_filename);
	cmd.Parse(argc, argv);

	uint16_t port = 0;
	switch(protocol) {
		case DnsDotDohProtocol::Do53:
			port = 53;
			break;
		case DnsDotDohProtocol::DoT:
			port = 853;
			break;
		case DnsDotDohProtocol::DoH:
			port = 443;
			break;
	}

	NS_LOG_INFO("Protocol: " << protocol);
	NS_LOG_INFO("Data Rate: " << datarate);
	NS_LOG_INFO("Latency: " << latency);
	NS_LOG_INFO("Loss: " << loss * 100 << "%");
	NS_LOG_INFO("Timeout: " << timeout.As(Time::S));

	Ptr<Node> clientN = CreateObject<Node>();
	Ptr<Node> recursorN = CreateObject<Node>();
	Ptr<Node> resourceServerN = CreateObject<Node>();

	NodeContainer dnsNc, httpNc, allNc;
	dnsNc.Add(clientN);
	dnsNc.Add(recursorN);
	httpNc.Add(clientN);
	httpNc.Add(resourceServerN);
	allNc.Add(clientN);
	allNc.Add(recursorN);
	allNc.Add(resourceServerN);

	PointToPointHelper dnsPtp, httpPtp;
	dnsPtp.SetDeviceAttribute("DataRate", StringValue(datarate));
	dnsPtp.SetChannelAttribute("Delay", StringValue(latency));
	httpPtp.SetDeviceAttribute("DataRate", StringValue(datarate));
	httpPtp.SetChannelAttribute("Delay", StringValue(latency));

	NetDeviceContainer dnsNdc, httpNdc;
	dnsNdc = dnsPtp.Install(dnsNc);
	httpNdc = httpPtp.Install(httpNc);

	Ptr<RateErrorModel> error = CreateObject<RateErrorModel>();
	error->SetUnit(RateErrorModel::ERROR_UNIT_PACKET);
	error->SetRate(DoubleValue(loss).Get());
	error->Enable();

	for (uint16_t i = 0; i < dnsNdc.GetN(); ++i) {
		Ptr<NetDevice> dev = dnsNdc.Get(i);
		dev->SetAttribute("ReceiveErrorModel", PointerValue(error));
	}

	for (uint16_t i = 0; i < httpNdc.GetN(); ++i) {
		Ptr<NetDevice> dev = httpNdc.Get(i);
		dev->SetAttribute("ReceiveErrorModel", PointerValue(error));
	}

	InternetStackHelper internet;
	internet.Install(allNc);

	Ipv4AddressHelper ipv4;
	ipv4.SetBase("10.1.1.0", "255.255.255.0");
	Ipv4InterfaceContainer dnsIic = ipv4.Assign(dnsNdc);

	ipv4.SetBase("10.1.2.0", "255.255.255.0");
	Ipv4InterfaceContainer httpIic = ipv4.Assign(httpNdc);

	ApplicationContainer apps;

	/* TODO Parse from file */
	auto requests = std::list<DnsDotDohRequest>();
	uint16_t id, depends_on;
	uint32_t request_length, response_length;
	float delay;
	std::string type;
	char comma;

	std::ifstream ifs;
	ifs.open(requests_filename);
	while(ifs.good() && !ifs.eof()) {
		/* Parse Format: id,depends_on,{DNS|HTTP},delay,request_length,response_length */
		ifs >> id >> comma >> depends_on >> comma;
		std::getline(ifs, type, ',');
		ifs >> delay >> comma >> request_length >> comma >> response_length;

		std::transform(type.begin(), type.end(), type.begin(), ::tolower);
		auto rtype = (type == "dns") ? DnsDotDohRequestType::DNS :
			(type == "http") ? DnsDotDohRequestType::HTTP :
			(throw std::runtime_error("invalid type: '" + type + "'"));

		auto r = DnsDotDohRequest(id, depends_on, rtype, delay, request_length, response_length);
		NS_LOG_INFO(r);
		requests.push_front(r);

		/* Check for newline */
		std::getline(ifs, type);
		ifs.peek();
	}
	ifs.close();

	DnsDotDohClientHelper client(dnsIic.GetAddress(1), port, protocol, httpIic.GetAddress(1), 80,
			timeout);
	apps = client.Install(clientN, requests);
	apps.Start(Seconds(0.0));
	apps.Stop(duration);

	DnsDotDohServerHelper recursor(dnsIic.GetAddress(1), port);
	apps = recursor.Install(recursorN);
	apps.Start(Seconds(0.0));
	apps.Stop(duration);

	DnsDotDohServerHelper resourceServer(httpIic.GetAddress(1), 80);
	apps = resourceServer.Install(resourceServerN);
	apps.Start(Seconds(0.0));
	apps.Stop(duration);

	Ipv4GlobalRoutingHelper::PopulateRoutingTables ();

#if PCAP
	dnsPtp.EnablePcapAll("dnsdotdoh-dns");
	httpPtp.EnablePcapAll("dnsdotdoh-http");
#endif

	Simulator::Stop(duration);
	Simulator::Run();
	Simulator::Destroy();

	return 0;
}
/* vim: set noet tw=100 ts=2 sw=2: */
