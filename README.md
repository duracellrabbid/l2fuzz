# L2Fuzz + SDPFuzz

A stateful fuzzer to detect vulnerabilities in Bluetooth BR/EDR Logical Link Control and Adaptation Protocol (L2CAP) layer.

SDPFuzz is an extension that builds on top of L2Fuzz to detect vulnerabilites in Service Discovery Protocol

## Prerequisites

L2Fuzz uses python3.6.9 and scapy 2.4.4. Also, it uses Bluetooth Dongle.

SDPFuzz is tested on Kali 2024.4 and Ubuntu 24.04. The Bluetooth Dongle used is a TP-Link Bluetooth dongle.

```
sudo apt-get install python3-pip
pip3 install scapy==2.4.4
sudo apt-get install libbluetooth-dev
sudo pip3 install git+https://github.com/pybluez/pybluez.git#egg=pybluez
pip3 install python-statemachine
pip3 install ouilookup
```

## Running the tests

1. move to L2Fuzz folder.
2. run the following command to update and run the latest scripts
```
sudo chmod +x run.sh
./run.sh
```
3. Choose target device.
```
Reset Bluetooth...
Performing classic bluetooth inquiry scan...

	Target Bluetooth Device List
	[No.]	[BT address]		  [Device name]		[Device Class]	  	[OUI]
	00.	AA:BB:CC:DD:EE:FF	  DESKTOP       	Desktop   	      	Vendor A
	01.	11:22:33:44:55:66	  Smartphone    	Smartphone	      	Vendor B
	Found 2 devices

Choose Device : 
```
4. Choose target service which is supported by L2CAP.

```
Start scanning services...

	List of profiles for the device
	00. [0x0000]: Service A
	01. [0x0001]: Service B
	02. [0x0002]: Service C
	03. [0x0003]: Service D
	04. [0x0004]: Service E
	05. [0x0005]: Service F
	
Select a profile to fuzz : 
```
5. Fuzz testing start.

### End test

```
Ctrl + C
```

### Log file

The log file will be generated after the fuzz testing in L2Fuzz folder.

## Paper

L2Fuzz paper is published in Jun 27, 2022 through "The 52nd Annual IEEE/IFIP International Conference on Dependable Systems and Networks".

Title : L2Fuzz: Discovering Bluetooth L2CAP Vulnerabilities Using Stateful Fuzz Testing

Paper : https://arxiv.org/abs/2208.00110

Video : https://youtu.be/lrc-mJTw1yM

Authors : Haram Park (Korea University), Carlos Nkuba Kayembe (Korea University), Seunghoon Woo (Korea University), Heejo Lee (Korea University)

Contacts : freehr94@korea.ac.kr, https://ccs.korea.ac.kr/
