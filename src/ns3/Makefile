all: docker

docker:
	docker build -t ns3-dnsdotdoh:latest .

run:
	docker run --rm -ti -v $$(pwd):/dnsdotdoh ns3-dnsdotdoh:latest /ns3/waf --run "dnsdotdoh --requests=/dnsdotdoh/example.rqst --protocol=Do53 --latency=5ms --loss=0.01 --datarate=1Mbps"
runpaul:
	docker run --rm -ti -v $$(pwd):/dnsdotdoh ns3-dnsdotdoh:latest /ns3/waf --run "dnsdotdoh --requests=/dnsdotdoh/temp.rqst --protocol=Do53 --latency=100ms --loss=0.01 --datarate=100Mbps"
