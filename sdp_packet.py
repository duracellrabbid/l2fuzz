import sys, os, subprocess
import json, datetime
from scapy.all import *
from scapy.packet import Packet
from random import *
from collections import OrderedDict
import struct
import uuid


REQ_PDU_ID = {
	0x02 : "SDP_SERVICE_SEARCH_REQ",
	0x04 : "SDP_SERVICE_ATTR_REQ",
	0x06 : "SDP_SERVICE_SEARCH_ATTR_REQ"
}

RSP_PDU_ID = {
	0x01 : "SDP_ERROR_RSP",
	0x03 : "SDP_SERVICE_SEARCH_RSP",
	0x05 : "SDP_SERVICE_ATTR_RSP",
	0x07 : "SDP_SERVICE_SEARCH_ATTR_RSP"
}


ERROR_RSP_CODE = {
	0x0001: "Invalid/unsupported SDP version",
	0x0002: "Invalid Service Record Handle",
	0x0003: "Invalid request syntax",
	0x0004: "Invalid PDU Size",
	0x0005: "Invalid Continuation State",
	0x0006: "Insufficient Resources to satisfy Request"
}

ASSIGNED_SERVICE_UUID = {
	"Service Discovery Server": "00001000-0000-1000-8000-00805f9b34fb",
	"Browse Group Descriptor": "00001001-0000-1000-8000-00805f9b34fb",
	"Public Browse Group": "00001002-0000-1000-8000-00805f9b34fb",
	"Serial Port": "00001101-0000-1000-8000-00805f9b34fb",
	"LAN Access Using PPP": "00001102-0000-1000-8000-00805f9b34fb",
	"Dial-up Networking": "00001103-0000-1000-8000-00805f9b34fb",
	"OBEX Object Push": "00001105-0000-1000-8000-00805f9b34fb",
	"OBEX File Transfer": "00001106-0000-1000-8000-00805f9b34fb",
	"Headset": "00001108-0000-1000-8000-00805f9b34fb",
	"Audio Source": "0000110A-0000-1000-8000-00805f9b34fb",
	"Audio Sink": "0000110B-0000-1000-8000-00805f9b34fb",
	"AV Remote Control Target": "0000110C-0000-1000-8000-00805f9b34fb",
	"AV Remote Control": "0000110E-0000-1000-8000-00805f9b34fb",
	"Handsfree": "0000111E-0000-1000-8000-00805f9b34fb",
	"Personal Area Networking User": "00001115-0000-1000-8000-00805f9b34fb",
	"Message Access Server": "00001132-0000-1000-8000-00805f9b34fb"
}

TYPE_DESCRIPTOR_CODE = {
	"NULL": 0x00,
	"Unsigned Integer": 0x01,
	"Signed two’s-complement integer": 0x02,
	"UUID": 0x03,
	"Text String": 0x04,
	"Boolean": 0x05,
	"Data Element Sequence": 0x06,
	"Data Element alternative": 0x07,
	"URL": 0x08
}

SIZE_DESCRIPTOR_CODE = {
	"1Byte": 0x00,
	"2Bytes": 0x01,
	"4Bytes": 0x02,
	"8Bytes": 0x03,
	"16Bytes": 0x04,
	"Data_Size_Additional_8_bits": 0x05,
	"Data_Size_Additional_16_bits": 0x06,
	"Data_Size_Additional_32_bits": 0x07
}


SERVICE_ATTRIBUTE_ID = {
	0x0000 : {
		"name":"ServiceRecordHandle",
		"type_code": TYPE_DESCRIPTOR_CODE["Unsigned Integer"],
		"size_code": SIZE_DESCRIPTOR_CODE["4Bytes"]
	},
	0x0001 : {
		"name":"ServiceClassIDList",
		"type_code": TYPE_DESCRIPTOR_CODE["Data Element Sequence"],
		"size_code": SIZE_DESCRIPTOR_CODE["Data_Size_Additional_16_bits"] #not sure, use 16 bits first
	},
	0x0002 : {
		"name":"ProviderName",
		"type_code": TYPE_DESCRIPTOR_CODE["Text String"],
		"size_code": SIZE_DESCRIPTOR_CODE["2Bytes"] #not sure, use 16 bits first
	},
	0x0003 : {
		"name":"ServiceID",
		"type_code": TYPE_DESCRIPTOR_CODE["UUID"],
		"size_code": SIZE_DESCRIPTOR_CODE["4Bytes"] #not sure, use 16 bits first
	},
	0x0004 : {
		"name":"ProtocolDescriptorList",
		"type_code": TYPE_DESCRIPTOR_CODE["Data Element Sequence"],
		"size_code": SIZE_DESCRIPTOR_CODE["Data_Size_Additional_16_bits"] #not sure, use 16 bits first
	},
	0x000D : {
		"name":"AdditionalProtocolDescriptorList",
		"type_code": TYPE_DESCRIPTOR_CODE["Data Element Sequence"],
		"size_code": SIZE_DESCRIPTOR_CODE["Data_Size_Additional_16_bits"] #not sure, use 16 bits first
	},
	0x0005 : {
		"name":"BrowseGroupList",
		"type_code": TYPE_DESCRIPTOR_CODE["Data Element Sequence"],
		"size_code": SIZE_DESCRIPTOR_CODE["Data_Size_Additional_16_bits"] #not sure, use 16 bits first
	},
	0x0006 : {
		"name":"LanguageBaseAttributeIDList",
		"type_code": TYPE_DESCRIPTOR_CODE["Data Element Sequence"],
		"size_code": SIZE_DESCRIPTOR_CODE["Data_Size_Additional_16_bits"] #not sure, use 16 bits first
	},
	0x0007 : {
		"name":"ServiceInfoTimeToLive",
		"type_code": TYPE_DESCRIPTOR_CODE["Unsigned Integer"],
		"size_code": SIZE_DESCRIPTOR_CODE["4Bytes"] #not sure, use 16 bits first
	},
	0x0008 : {
		"name":"ServiceAvailability",
		"type_code": TYPE_DESCRIPTOR_CODE["Unsigned Integer"],
		"size_code": SIZE_DESCRIPTOR_CODE["1Byte"] #not sure, use 16 bits first
	},
	0x0009 : {
		"name":"BluetoothProfileDescriptorList",
		"type_code": TYPE_DESCRIPTOR_CODE["Data Element Sequence"],
		"size_code": SIZE_DESCRIPTOR_CODE["Data_Size_Additional_16_bits"] #not sure, use 16 bits first
	},
	0x000A : {
		"name":"DocumentationURL",
		"type_code": TYPE_DESCRIPTOR_CODE["URL"],
		"size_code": SIZE_DESCRIPTOR_CODE["16Bytes"] #not sure, use 16 bits first
	},
	0x000B : {
		"name":"ClientExecutableURL",
		"type_code": TYPE_DESCRIPTOR_CODE["URL"],
		"size_code": SIZE_DESCRIPTOR_CODE["16Bytes"] #not sure, use 16 bits first
	},
	0x000C : {
		"name":"IconURL",
		"type_code": TYPE_DESCRIPTOR_CODE["URL"],
		"size_code": SIZE_DESCRIPTOR_CODE["16Bytes"] #not sure, use 16 bits first
	},
}



# helper function to build prot descriptor header
# idea is to have a unified area to build in case protocol spec changes 
def build_prot_descriptor_header(type_code, size_code):
	return type_code << 3 | size_code

def build_attr_id_struct(attr_id, isRange=False):
	print(f"Attr Id: {attr_id}")
	attr_type_code = TYPE_DESCRIPTOR_CODE["Unsigned Integer"]
	attr_size_code = SIZE_DESCRIPTOR_CODE["2Bytes"] if not isRange else SIZE_DESCRIPTOR_CODE["4Bytes"]
	elem_type = build_prot_descriptor_header(attr_type_code, attr_size_code)
	value = struct.pack(">H", attr_id) if not isRange else struct.pack(">I", attr_id)
	attr_struct = struct.pack("B", elem_type) + value
	return attr_struct

def build_uuid_struct(uuid_str):
	print(f"UUID: {uuid_str}")
	uuid_type_code = TYPE_DESCRIPTOR_CODE["UUID"]
	uuid_size_code = SIZE_DESCRIPTOR_CODE["2Bytes"]
	uuid_obj = uuid.UUID(uuid_str)
	print(f"UUID obj: {uuid_obj}")
	# Determine UUID type and size
	if uuid_obj.version == 4:  # 128-bit UUID
		print("UUID is 128bits")
		uuid_size_code = SIZE_DESCRIPTOR_CODE["16Bytes"]
		elem_type = build_prot_descriptor_header(uuid_type_code, uuid_size_code)
		value = uuid_obj.bytes
	else:  # 16/32-bit UUID
		print("UUID is not 128 bits")
		short_uuid = uuid_obj.int >> 96
		if short_uuid <= 0xFFFF:
			print("16 bits")
			elem_type = build_prot_descriptor_header(uuid_type_code, uuid_size_code)
			value = struct.pack(">H", short_uuid)
		else:
			print("32 bits")
			uuid_size_code = SIZE_DESCRIPTOR_CODE["4Bytes"]
			elem_type = build_prot_descriptor_header(uuid_type_code, uuid_size_code)
			value = struct.pack(">I", short_uuid)
			
	uuid_struct = struct.pack("B", elem_type) + value
	return uuid_struct

def build_sdp_service_search_attr_request(tid=0x0001, uuid_list=[ASSIGNED_SERVICE_UUID["Service Discovery Server"]],max_attr_byte_count=0x0007, attribute_list=[{"attribute_id":0x0001, "isRange":False}] ):
	#1) build search pattern first
	service_search_pattern = build_sdp_search_pattern(uuid_list)
 
	#2) build attribute pattern
	attribute_pattern = build_attribute_list_pattern(attribute_list)
 
	#3) calculate length, should be len(ssp) + len(ap) + len(max_attr_count) + len(continuation_state)
	pattern_length = len(service_search_pattern) + len(attribute_pattern) + 3
	
	#4) Build the struct for max_attr_count first
	max_attr_byte_count_pattern = struct.pack(">H", max_attr_byte_count)
 
	#put header together
	pdu_header = struct.pack(">BHH",
							0x06,
							tid,
							pattern_length
							)
 
	continuation = b"\x00"
	return pdu_header + service_search_pattern + max_attr_byte_count_pattern + attribute_pattern + continuation
 
	

def build_attribute_list_pattern(attribute_list=[{"attribute_id":0x0001, "isRange":False}]):
	data_seq_type_code = TYPE_DESCRIPTOR_CODE["Data Element Sequence"]
	data_seq_size_code = SIZE_DESCRIPTOR_CODE["Data_Size_Additional_8_bits"]
	data_seq_header = struct.pack("B",build_prot_descriptor_header(data_seq_type_code, data_seq_size_code))
	data_elements = []
	for attr_id in attribute_list:
		if "attribute_id" in attr_id:
			isRange = attr_id["isRange"] if "isRange" in attr_id else False
			attr_struct = build_attr_id_struct(attr_id["attribute_id"], isRange)
			data_elements.append(attr_struct)
	elements_payload = b"".join(data_elements)
	payload_len = len(elements_payload)
	seq_header = data_seq_header + struct.pack(">B", payload_len)
	attribute_pattern = seq_header + elements_payload
	return attribute_pattern

def build_sdp_service_attr_request(tid=0x0001, service_record_handle=0x0001, max_attr_byte_count=0x0007, attribute_list=[{"attribute_id":0x0001, "isRange":False}]):
	attribute_pattern = build_attribute_list_pattern(attribute_list)
	
	pdu_header = struct.pack(">BHHIH",
							 0x04,
							 tid,
							 len(attribute_pattern) + 7,
							 service_record_handle,
							 max_attr_byte_count)
	continuation = b"\x00"
	
	
	return pdu_header + attribute_pattern + continuation

def build_sdp_search_pattern(uuid_list):
	data_elements = []
	data_seq_type_code = TYPE_DESCRIPTOR_CODE["Data Element Sequence"]
	data_seq_size_code = SIZE_DESCRIPTOR_CODE["Data_Size_Additional_8_bits"]
	data_seq_header = struct.pack("B",build_prot_descriptor_header(data_seq_type_code, data_seq_size_code))
	
	for uuid_str in uuid_list:
		uuid_struct = build_uuid_struct(uuid_str)	   
		data_elements.append(uuid_struct)
		
	# 2. Build Data Element Sequence
	elements_payload = b"".join(data_elements)
	payload_len = len(elements_payload)
	#seq_len = len(elements_payload) + 3
	seq_header = data_seq_header + struct.pack(">B", payload_len) 
	service_search_pattern = seq_header + elements_payload
	return service_search_pattern

def build_sdp_search_request(tid=0x0001, max_record=10, uuid_list=[ASSIGNED_SERVICE_UUID["Service Discovery Server"]]):
	# 1. Build Data Elements
	
	service_search_pattern = build_sdp_search_pattern(uuid_list)

	# 3. Build SDP Request
	pdu_header = struct.pack(">BHH", 
						   0x02,  # PDU ID
						   tid,  # Transaction ID
						   len(service_search_pattern) + 3)  # plen
	
	max_records = struct.pack(">H", max_record)  # Max service records
	continuation = b"\x00"  # No continuation state

	return pdu_header + service_search_pattern + max_records + continuation


def parse_sdp_response(response):
	# Basic response parsing
	ret_data = {
		"handle_list": None,
		"attribute_list": None
	}
	try:
		pdu_id = response[0]
		if pdu_id == 0x03:
			tid = struct.unpack(">H", response[1:3])[0]
			plen = struct.unpack(">H", response[3:5])[0]
			total_records = struct.unpack(">H", response[5:7])[0]
			current_records = struct.unpack(">H", response[7:9])[0]
			
			print(f"SDP Response (TID: {tid:04x})")
			print(f"Total Records: {total_records}")
			print(f"Current Records: {current_records}")
			
			# Parse handle list
			handle_data = response[9:]  # Skip continuation state
			print(f"Handle data: {handle_data}")
			start_index = 0
			next_index = 0
			handle_list = []
			for curr_index in range(current_records):
				start_index = curr_index * 4
				next_index = start_index + 4
				handle_raw = handle_data[start_index:next_index]
				print(f"Handle raw:{handle_raw}")
				handle_id = struct.unpack(">I", handle_raw)
				handle_list.append(handle_id[0])
				print(f"Handle record {curr_index+1}: {handle_id[0]:08x}")
			continuation_state = handle_data[next_index:]
			ret_data["handle_list"] = handle_list
			print(f"Continuation state: {continuation_state}")
		elif pdu_id == 0x05:
			print("Service attribute response")
			pass
		else: #SDP Response Error
			print("SDP Response error")
		
	except Exception as e:
		print(f"Parse error: {str(e)}")
	return ret_data
		
