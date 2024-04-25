#!/usr/bin/python -O
"""
[Amun - low interaction honeypot]
Copyright (C) [2008]  [Jan Goebel]

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, see <http://www.gnu.org/licenses/>
"""

try:
	import psyco ; psyco.full()
	from psyco.classes import *
except ImportError:
	pass

import socket
import struct
import sys
import time

import amun_logging

class amun_smb_prot:
	def __init__(self):
		### variables
		self.findDialect = '\x02NT LM 0.12'
		self.SMB_LEN0 = 2
		self.SMB_LEN1 = 3
		self.SMB_COMMAND = 8
		self.SMB_ERRCLASS = 9
		self.SMB_ERRCODE0 = 11
		self.SMB_ERRCODE1 = 12
		self.SMB_FLAG = 13
		self.SMB_FLAG0 = 14
		self.SMB_FLAG1 = 15
		self.SMB_TREEID0 = 28
		self.SMB_TREEID1 = 29
		self.SMB_PID0 = 30
		self.SMB_PID1 = 31
		self.SMB_UID0 = 32
		self.SMB_UID1 = 33
		self.SMB_MID0 = 34
		self.SMB_MID1 = 35
		self.SMB_WORDCOUNT = 36
		self.SMB_PACKETTYPE = 62
		self.NUM_COUNT_ITEMS = 12 
		self.setCountItems = 1
		### netbios header (byte 3 und 4 bestimmen die smb length)
		self.net_header = "\x00\x00\x00\x57"
		### smb header - flag[13]=\x98
		self.smb_header = "\xff\x53\x4d\x42\x72\x00\x00\x00\x00\x98\x01\x28\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
		### parameter block starting with word count
		self.param_block = "\x11"
		### data block starting with byte count
		self.data_block = "\x00\x00"
		### native OS: Windows 5.1
		self.native_os = "\x57\x69\x6e\x64\x6f\x77\x73\x20\x35\x2e\x31\x00"
		### native LAN manager: Windows 2000 LAN Manager
		self.native_lan_man = "\x57\x69\x6e\x64\x6f\x77\x73\x20\x32\x30\x30\x30\x20\x4c\x41\x4e\x20\x4d\x61\x6e\x61\x67\x65\x72\x20\x00"
		### primary domain: WORKGROUP
		self.prim_domain1 = "\x57\x00\x4f\x00\x52\x00\x4b\x00\x47\x00\x52\x00\x4f\x00\x55\x00\x50\x00\x00\x00"
		self.prim_domain2 = "\x57\x4f\x52\x4b\x47\x52\x4f\x55\x50\x00"
		### server name
		self.server_name = "\x54\x00\x45\x00\x53\x00\x54\x00\x00\x00"
		### FID
		self.fid_len = "\x00\x40"
		self.create_action = "\x00\x00\x00\x00"
		self.created     = "\x00\x00\x00\x00\x00\x00\x00\x00"
		self.last_access = "\x00\x00\x00\x00\x00\x00\x00\x00"
		self.last_write  = "\x00\x00\x00\x00\x00\x00\x00\x00"
		self.last_change = "\x00\x00\x00\x00\x00\x00\x00\x00"
		self.file_attrib = "\x80\x00\x00\x00"
		self.alloc_size  = "\x00\x10\x00\x00\x00\x00\x00\x00"
		self.endof_file  = "\x00\x00\x00\x00\x00\x00\x00\x00"
		self.file_type   = "\x02\x00"
		self.ipc_state   = "\xff\x05"
		self.is_directory = "\x00"
		self.fid_data = "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9b\x01\x12\x00\x9b\x01\x12\x00\x00\x00"
		### session setup andx data
		self.session_data = "\xa1\x81\xe80\x81\xe5\xa0\x03\n\x01\x01\xa1\x0c\x06\n+\x06\x01\x04\x01\x827\x02\x02\n\xa2\x81\xcf\x04\x81\xccNTLMSSP\x00\x02\x00\x00\x00\x18\x00\x18\x008\x00\x00\x00\x05\x02\x8a\x02\xbb\xdf\xa0`>U\x0e\xba\x00\x00\x00\x00\x00\x00\x00\x00|\x00|\x00P\x00\x00\x00\x05\x01(\n\x00\x00\x00\x0fT\x00K\x00S\x00-\x00A\x00T\x00T\x00A\x00C\x00K\x00E\x00R\x00\x02\x00\x18\x00T\x00K\x00S\x00-\x00A\x00T\x00T\x00A\x00C\x00K\x00E\x00R\x00\x01\x00\x18\x00T\x00K\x00S\x00-\x00A\x00T\x00T\x00A\x00C\x00K\x00E\x00R\x00\x04\x00\x18\x00t\x00k\x00s\x00-\x00a\x00t\x00t\x00a\x00c\x00k\x00e\x00r\x00\x03\x00\x18\x00t\x00k\x00s\x00-\x00a\x00t\x00t\x00a\x00c\x00k\x00e\x00r\x00\x06\x00\x04\x00\x01\x00\x00\x00\x00\x00\x00\x00"
		self.session_data_Stage2 = "\xa1\x81\xac\x30\x81\xa9\xa0\x03\x0a\x01\x01\xa1\x0c\x06\x0a\x2b\x06\x01\x04\x01\x82\x37\x02\x02\x0a\xa2\x81\x93\x04\x81\x90\x4e\x54\x4c\x4d\x53\x53\x50\x00\x02\x00\x00\x00\x0c\x00\x0c\x00\x38\x00\x00\x00\x05\x02\x8a\x02\x84\x06\xfa\xc1\xa5\x53\xbe\x7d\x00\x00\x00\x00\x00\x00\x00\x00\x4c\x00\x4c\x00\x44\x00\x00\x00\x05\x01\x28\x0a\x00\x00\x00\x0f\x54\x00\x45\x00\x53\x00\x54\x00\x58\x00\x50\x00\x02\x00\x0c\x00\x54\x00\x45\x00\x53\x00\x54\x00\x58\x00\x50\x00\x01\x00\x0c\x00\x54\x00\x45\x00\x53\x00\x54\x00\x58\x00\x50\x00\x04\x00\x0c\x00\x74\x00\x65\x00\x73\x00\x74\x00\x78\x00\x70\x00\x03\x00\x0c\x00\x74\x00\x65\x00\x73\x00\x74\x00\x78\x00\x70\x00\x06\x00\x04\x00\x01\x00\x00\x00\x00\x00\x00\x00\x57\x69\x6e\x64\x6f\x77\x73\x20\x35\x2e\x31\x00\x57\x69\x6e\x64\x6f\x77\x73\x20\x32\x30\x30\x30\x20\x4c\x41\x4e\x20\x4d\x61\x6e\x61\x67\x65\x72\x00"
		### read andx data
		self.read_data = "\x05\x00\x0c\x03\x10\x00\x00\x00|\x01\x00\x00\x00\x00\x00\x00\xb8\x10\xb8\x10\xdda\x00\x00\x0e\x00\\PIPE\\browser\x00\x0e\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00"
		self.read_data2 = "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04]\x88\x8a\xeb\x1c\xc9\x11\x9f\xe8\x08\x00\x10\x02\x00\x00\x00"
		self.read_data_contextitem = "\x02\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
		self.read_last_data_contextitem = "\x00\x00\x00\x00\x04\x5d\x88\x8a\xeb\x1c\xc9\x11\x9f\xe8\x08\x00\x2b\x10\x48\x60\x02\x00\x00\x00"
		### reply packet
		self.reply = []
		### Stage
		self.stage = "MS08067_STAGE2"

	def setStage(self,stage):
		self.stage = stage
		return
		
	def setDialect(self, type):
		if type=='ntlm':
			self.findDialect = '\x02NT LM 0.12'
		elif type=='lanman':
			self.findDialect = '\x02LANMAN1.0'
		else:
			self.findDialect = '\x02NT LM 0.12'
		return

	def print_message(self, data):
		print "\n"
		counter = 1
		for byte in data:
			if counter==16:
				ausg = hex(struct.unpack('B',byte)[0])
				if len(ausg) == 3:
					list = str(ausg).split('x')
					ausg = "%sx0%s" % (list[0],list[1])
					print ausg
				else:
					print ausg
				counter = 0
			else:
				ausg = hex(struct.unpack('B',byte)[0])
				if len(ausg) == 3:
					list = str(ausg).split('x')
					ausg = "%sx0%s" % (list[0],list[1])
					print ausg,
				else:
					print ausg,
			counter += 1
		print "\n>> Incoming Codesize: %s\n\n" % (len(data))
		return

	def checkForNetbiosSessionRequest(self, data):
		try:
			type = data[0]
			flags = data[1]
			size = struct.unpack('2B', data[2:4])[1]
			rest = data[4:]
			### session request
			if type=='\x81' and len(rest)==size:
				return True
			else:
				return False
		except:
			return False
		return False

	def checkForNetbiosSessionRetargetRequest(self, data):
		try:
			type = data[0]
			flags = data[1]
			size = struct.unpack('2B', data[2:4])[1]
			rest = data[4:]
			### retarget request
			if type=='\x85' and len(rest)==size:
				return True
			else:
				return False
		except:
			return False
		return False

	def NetbiosRetargetReply(self, mesdata, ownIP):
		self.reply = []
		self.reply.append('\x84')
		self.reply.append('\x00')
		self.reply.append('\x00')
		self.reply.append('\x00')
		fill = ['\x00'] * 6
		self.reply.extend(fill)

		iprepr = socket.inet_aton(ownIP)
		self.reply[4:8] = iprepr

		self.reply[8] = '\x00'
		self.reply[9] = '\x8b'

		return

	def NetbiosSessionReply(self, mesdata):
		self.reply = []
		self.reply.append('\x82')
		self.reply.append('\x00')
		self.reply.append('\x00')
		self.reply.append('\x00')
		return

	def checkForSMBPacket(self, data):
		try:
			smbPart = data[4:8]
			if smbPart == '\xff\x53\x4d\x42':
				return True
			else:
				return False
		except:
			return False
		return False

	def getsmbNegotInfo(self, message):
		wordCount = struct.unpack('!B', message[self.SMB_WORDCOUNT])[0]
		if wordCount==0:
			bytePosition = self.SMB_WORDCOUNT+1
			byteCount = struct.unpack('!H', message[bytePosition:bytePosition+2])[0]
		else:
			bytePosition = self.SMB_WORDCOUNT+wordCount+1
			byteCount = struct.unpack('!H', message[bytePosition:bytePosition+2])[0]
		allDialects = message[bytePosition+2:].split('\x00')
		for item in allDialects:
			if item == '':
				allDialects.remove(item)
		for i in range(0, len(allDialects)):
			if allDialects[i] == '\x02LANMAN1.0':
				return i
			if allDialects[i] == '\x02NT LM 0.12':
				return i
		return None

	def smbNegotReply(self, message, dialectIndex):
		self.reply = []
		self.reply.extend(list(self.net_header))
		self.reply.extend(list(self.smb_header))

		self.reply[self.SMB_FLAG] = '\x98'
		self.reply[self.SMB_FLAG0] = '\x01'
		self.reply[self.SMB_FLAG1] = '\x28'

		self.reply[self.SMB_PID0] = message[self.SMB_PID0]
		self.reply[self.SMB_PID1] = message[self.SMB_PID1]
		
		self.reply[self.SMB_MID0] = message[self.SMB_MID0]
		self.reply[self.SMB_MID1] = message[self.SMB_MID1]

		fill = ['\x00'] * 53
		self.reply.extend(fill)

		### word count - \x11 = NT LM 0.12
		self.reply[36] = "\x11"
		###### parameter block
		### dialect
		if dialectIndex == None:
			self.reply[37] = "\x05"
			self.reply[38] = "\x00"
		else:
			#dialectHex = struct.pack('!H', dialectIndex)
			#self.reply[37:39] = dialectHex
			self.reply[37] = "\x03"
			self.reply[38] = "\x00"
		### securityMode
		self.reply[39] = "\x03"
		### max mpx count
		self.reply[40] = "\x0a"
		self.reply[41] = "\x00"
		### max vcs
		self.reply[42] = "\x01"
		self.reply[43] = "\x00"
		### max buffer size
		self.reply[44] = "\x04"
		self.reply[45] = "\x11"
		self.reply[46] = "\x00"
		self.reply[47] = "\x00"
		### max raw
		self.reply[48] = "\x00"
		self.reply[49] = "\x00"
		self.reply[50] = "\x01"
		self.reply[51] = "\x00"
		### session key
		self.reply[52] = "\x00"
		self.reply[53] = "\x00"
		self.reply[54] = "\x00"
		self.reply[55] = "\x00"
		### capabilities
		self.reply[56] = "\xfd"
		self.reply[57] = "\xe3"
		self.reply[58] = "\x00"
		self.reply[59] = "\x80"
		### system time high
		### generate time string
		smbtime = struct.pack('Q' , ( (time.time()+11644473600)*10000000 ) )
		self.reply[60:68] = smbtime
		### server time zone
		self.reply[68] = "\x88"
		self.reply[69] = "\xff"
		### encryptedkey lenght
		self.reply[70] = "\x00"
		### byte count
		self.reply[71] = "\x00"
		self.reply[72] = "\x00"
		self.reply[73] = "\xf8"
		self.reply[74] = "\xbc"
		self.reply[75] = "\xe6"
		self.reply[76] = "\x3a"
		self.reply[77] = "\x7c"
		self.reply[78] = "\x02"
		self.reply[79] = "\x4b"
		self.reply[80] = "\x4f"
		self.reply[81] = "\x84"
		self.reply[82] = "\xc0"
		self.reply[83] = "\xb9"
		self.reply[84] = "\x5b"
		self.reply[85] = "\xe0"
		self.reply[86] = "\x4b"
		self.reply[87] = "\x82"
		self.reply[88] = "\x55"
		
		### calc byte count
		bytecount = struct.pack('H', len(self.reply[73:]))
		self.reply[71:73] = bytecount
		###
		pktlength = struct.pack('!H', (len(self.reply)-4))
		self.reply[2:4] = pktlength
		return

	def smbSessionAndXReply(self, message):
		if self.stage == "MS08067_STAGE2":
			#print "Stage2 Done"
			self.reply = []
			self.reply.extend(list(self.net_header))
			self.reply.extend(list(self.smb_header))
			
			self.reply[self.SMB_COMMAND] = "\x73"
			
			self.reply[self.SMB_ERRCLASS] = "\x16"
			self.reply[self.SMB_ERRCODE1] = "\xc0"
			
			self.reply[self.SMB_FLAG] = '\x98'
			self.reply[self.SMB_FLAG0] = "\x01"
			self.reply[self.SMB_FLAG1] = "\x68"
			
			self.reply[self.SMB_TREEID0] = message[self.SMB_TREEID0]
			self.reply[self.SMB_TREEID1] = message[self.SMB_TREEID1]
			
			self.reply[self.SMB_PID0] = message[self.SMB_PID0]
			self.reply[self.SMB_PID1] = message[self.SMB_PID1]
			
			self.reply[self.SMB_UID0] = "\x01"
			self.reply[self.SMB_UID1] = "\x08"
			
			self.reply[self.SMB_MID0] = message[self.SMB_MID0]
			self.reply[self.SMB_MID1] = message[self.SMB_MID1]

			self.reply.extend((['\x00'] * 11))
			### byte count
			self.reply[36] = "\x04"
			### andxcommand
			self.reply[37] = "\xff"
			### reserved
			self.reply[38] = "\x00"
			### anxoffset
			self.reply[39] = "\xff"
			self.reply[40] = "\x00"
			### action
			self.reply[41] = "\x00"
			self.reply[42] = "\x00"
			### Security Blob
			self.reply[43] = "\xaf"
			self.reply[44] = "\x00"
			### byte count
			self.reply[45] = "\x00"
			self.reply[46] = "\x00"
			###
			self.reply.extend(list(self.session_data_Stage2))
	
			### calc byte count
			bytecount = struct.pack('H', len(self.reply[47:]))
			self.reply[45:47] = bytecount
	
			###
			pktlength = struct.pack('!H', (len(self.reply)-4))
			self.reply[2:4] = pktlength
			return
			
		if self.stage == "MS08067_STAGE3":
			#print "Stage3 Done"
			self.reply = []
			self.reply.extend(list(self.net_header))
			self.reply.extend(list(self.smb_header))
			
			self.reply[self.SMB_COMMAND] = "\x73"
			
			self.reply[self.SMB_ERRCLASS] = "\x6d"
			self.reply[self.SMB_ERRCODE1] = "\xc0"
			
			self.reply[self.SMB_FLAG] = '\x98'
			self.reply[self.SMB_FLAG0] = "\x01"
			self.reply[self.SMB_FLAG1] = "\x68"
			
			self.reply[self.SMB_TREEID0] = message[self.SMB_TREEID0]
			self.reply[self.SMB_TREEID1] = message[self.SMB_TREEID1]
			
			self.reply[self.SMB_PID0] = message[self.SMB_PID0]
			self.reply[self.SMB_PID1] = message[self.SMB_PID1]
			
			self.reply[self.SMB_UID0] = "\x01"
			self.reply[self.SMB_UID1] = "\x08"
			
			self.reply[self.SMB_MID0] = message[self.SMB_MID0]
			self.reply[self.SMB_MID1] = message[self.SMB_MID1]
			
			fill = ['\x00'] * 3
			self.reply.extend(fill)
			
			self.reply[36] = "\x00"
			### andxcommand
			self.reply[37] = "\x00"
			### reserved
			self.reply[38] = "\x00"
			
			pktlength = struct.pack('!H', (len(self.reply)-4))
			self.reply[2:4] = pktlength
			return	
		
		if self.stage == "MS08067_STAGE4":
			#print "Stage4 Done"
			self.reply = []
			self.reply.extend(list(self.net_header))
			self.reply.extend(list(self.smb_header))

			self.reply[self.SMB_COMMAND] = "\x73"
		
			self.reply[self.SMB_ERRCLASS] = "\x00"
			self.reply[self.SMB_ERRCODE1] = "\x00"

			self.reply[self.SMB_FLAG] = '\x98'
			self.reply[self.SMB_FLAG0] = "\x01"
			self.reply[self.SMB_FLAG1] = "\x20"

			self.reply[self.SMB_TREEID0] = message[self.SMB_TREEID0]
			self.reply[self.SMB_TREEID1] = message[self.SMB_TREEID1]

			self.reply[self.SMB_PID0] = message[self.SMB_PID0]
			self.reply[self.SMB_PID1] = message[self.SMB_PID1]

			self.reply[self.SMB_UID0] = "\x01"
			self.reply[self.SMB_UID1] = "\x08"

			self.reply[self.SMB_MID0] = message[self.SMB_MID0]
			self.reply[self.SMB_MID1] = message[self.SMB_MID1]

			fill = ['\x00'] * 9
			self.reply.extend(fill)

			### word count
			self.reply[36] = "\x03"
			###### parameter block
			### andxcommand
			self.reply[37] = "\xff"
			### reserved
			self.reply[38] = "\x00"
		    ### anxoffset
			self.reply[39] = "\x5c"
			self.reply[40] = "\x00"
			### action
			self.reply[41] = "\x00"
			self.reply[42] = "\x00"
			### byte count
			self.reply[43] = "\x00"
			self.reply[44] = "\x00"
			###
			self.reply.extend(list(self.native_os))
			self.reply.extend(list(self.native_lan_man))
			self.reply.extend(list(self.prim_domain2))
			### calc byte count
			bytecount = struct.pack('H', len(self.reply[45:]))
			self.reply[43:45] = bytecount
			###
			pktlength = struct.pack('!H', (len(self.reply)-4))
			self.reply[2:4] = pktlength
			return
		else:	
			self.reply = []
			self.reply.extend(list(self.net_header))
			self.reply.extend(list(self.smb_header))

			self.reply[self.SMB_COMMAND] = "\x73"
		
			self.reply[self.SMB_ERRCLASS] = "\x00"
			self.reply[self.SMB_ERRCODE1] = "\x00"

			self.reply[self.SMB_FLAG] = '\x88'
			self.reply[self.SMB_FLAG0] = "\x00"
			self.reply[self.SMB_FLAG1] = "\x00"

			self.reply[self.SMB_TREEID0] = message[self.SMB_TREEID0]
			self.reply[self.SMB_TREEID1] = message[self.SMB_TREEID1]

			self.reply[self.SMB_PID0] = message[self.SMB_PID0]
			self.reply[self.SMB_PID1] = message[self.SMB_PID1]

			self.reply[self.SMB_UID0] = "\x01"
			self.reply[self.SMB_UID1] = "\x08"

			self.reply[self.SMB_MID0] = message[self.SMB_MID0]
			self.reply[self.SMB_MID1] = message[self.SMB_MID1]

			fill = ['\x00'] * 9
			self.reply.extend(fill)

			### word count
			self.reply[36] = "\x03"
			###### parameter block
			### andxcommand
			self.reply[37] = "\xff"
			### reserved
			self.reply[38] = "\x00"
			### anxoffset
			self.reply[39] = "\x58"
			self.reply[40] = "\x00"
			### action
			self.reply[41] = "\x00"
			self.reply[42] = "\x00"
			### byte count
			self.reply[43] = "\x00"
			self.reply[44] = "\x00"
			###
			self.reply.extend(list(self.native_os))
			self.reply.extend(list(self.native_lan_man))
			self.reply.extend(list(self.prim_domain2))
	
			### calc byte count
			bytecount = struct.pack('H', len(self.reply[45:]))
			self.reply[43:45] = bytecount
	
			###
			pktlength = struct.pack('!H', (len(self.reply)-4))
			self.reply[2:4] = pktlength
			return
	def smbTreeConnectReply(self, message):
		self.reply = []
		self.reply.extend(list(self.net_header))
		self.reply.extend(list(self.smb_header))
		
		self.reply[self.SMB_COMMAND] = "\x75"

		self.reply[self.SMB_ERRCLASS] = "\x00"
		self.reply[self.SMB_ERRCODE1] = "\x00"

		self.reply[self.SMB_FLAG1] = "\x20"

		self.reply[self.SMB_TREEID0] = "\x00"
		self.reply[self.SMB_TREEID1] = "\x08"

		self.reply[self.SMB_PID0] = message[self.SMB_PID0]
		self.reply[self.SMB_PID1] = message[self.SMB_PID1]

		self.reply[self.SMB_UID0] = "\x01"
		self.reply[self.SMB_UID1] = "\x08"

		self.reply[self.SMB_MID0] = message[self.SMB_MID0]
		self.reply[self.SMB_MID1] = message[self.SMB_MID1]

		fill = ['\x00'] * 14
		self.reply.extend(fill)

		### word count
		self.reply[36] = "\x03"
		### andx command
		self.reply[37] = "\xff"
		### reserved
		self.reply[38] = "\x00"
		### andx offset
		self.reply[39] = "\x2e"
		self.reply[40] = "\x00"
		### optional support
		self.reply[41] = "\x01"
		self.reply[42] = "\x00"
		### byte count
		self.reply[43] = "\x05"
		self.reply[44] = "\x00"
		### service
		self.reply[45] = "\x49"
		self.reply[46] = "\x50"
		self.reply[47] = "\x43"
		self.reply[48] = "\x00"
		### native filesystem
		self.reply[49] = "\x00"
		###
		pktlength = struct.pack('!H', (len(self.reply)-4))
		self.reply[2:4] = pktlength
		return

	def smbNTCreateReply(self, message):
		self.reply = []
		self.reply.extend(list(self.net_header))
		self.reply.extend(list(self.smb_header))
		
		self.reply[self.SMB_COMMAND] = "\xa2"

		self.reply[self.SMB_ERRCLASS] = "\x00"
		self.reply[self.SMB_ERRCODE1] = "\x00"

		self.reply[self.SMB_FLAG0] = "\x01"
		self.reply[self.SMB_FLAG1] = "\x20"
		
		self.reply[self.SMB_TREEID0] = "\x00"
		self.reply[self.SMB_TREEID1] = "\x08"

		self.reply[self.SMB_PID0] = message[self.SMB_PID0]
		self.reply[self.SMB_PID1] = message[self.SMB_PID1]

		self.reply[self.SMB_UID0] = "\x01"
		self.reply[self.SMB_UID1] = "\x08"

		self.reply[self.SMB_MID0] = message[self.SMB_MID0]
		self.reply[self.SMB_MID1] = message[self.SMB_MID1]

		fill = ['\x00'] * 6
		self.reply.extend(fill)

		### word count
		self.reply[36] = "\x2a"
		### andx command
		self.reply[37] = "\xff"
		### reserved
		self.reply[38] = "\x00"
		### andx offset
		self.reply[39] = "\x87"
		self.reply[40] = "\x00"
		### op lock level
		self.reply[41] = "\x00"
		### FID
		self.reply.extend(list(self.fid_len))
		### create action
		self.reply.extend(list(self.create_action))
		### created
		self.reply.extend(list(self.created))
		### last access
		self.reply.extend(list(self.last_access))
		### last write
		self.reply.extend(list(self.last_write))
		### change
		self.reply.extend(list(self.last_change))
		### file attributes 
		self.reply.extend(list(self.file_attrib))
		### allocation size
		self.reply.extend(list(self.alloc_size))
		### end of file
		self.reply.extend(list(self.endof_file))
		### file type
		self.reply.extend(list(self.file_type))
		### ipc state
		self.reply.extend(list(self.ipc_state))
		### directory
		self.reply.extend(list(self.is_directory))
		### byte count
		self.reply.append("\x00")
		self.reply.append("\x00")
		### fid
		self.reply.extend(list(self.fid_data))
		###
		pktlength = struct.pack('!H', (len(self.reply)-4))
		self.reply[2:4] = pktlength
		return

	def examineTransaction(self, message):
		wordCount = struct.unpack('!B', message[self.SMB_WORDCOUNT])[0]
		parameter = message[self.SMB_WORDCOUNT+1:]
		print "wordcount: %s" % ([wordCount])
		print [parameter]
		print "totalparametercount: %s" % ([parameter[0:2]])
		print "totaldatacount: %s" % ([parameter[2:4]])
		print "maxparametercount: %s" % ([parameter[4:6]])
		print "maxdatacount: %s" % ([parameter[6:8]])
		print "maxsetupcount: %s" % ([parameter[8]])
		print "reserved: %s" % ([parameter[9]])
		print "flags: %s" % ([parameter[10:12]])
		print "timeout: %s" % ([parameter[12:16]])
		print "reserved2: %s" % ([parameter[16:18]])
		print "parametercount: %s" % ([parameter[18:20]])
		print "parameteroffset: %s" % ([parameter[20:22]])
		print "datacount: %s" % ([parameter[22:24]])
		print "dataoffset: %s" % ([parameter[24:26]])
		print "setupcount: %s" % ([parameter[26]])
		print "reserved3: %s" % ([parameter[27]])
		print "setup: %s" % ([parameter[28:30]])
		if parameter[28]=='\x26':
			print "TransactNmPipe 0x26 write/read operation on pipe requested"
	
		byteCount = struct.unpack('!H', parameter[30:32])
		databytes = parameter[32:]
		print "bytecount: %s" % (byteCount)
		print [databytes]
		print len(databytes)
		return

	def smbTransaction(self, message):
		self.reply = []
		self.reply.extend(list(self.net_header))
		self.reply.extend(list(self.smb_header))
		
		self.reply[self.SMB_COMMAND] = "\x25"

		self.reply[self.SMB_ERRCLASS] = "\x00"
		self.reply[self.SMB_ERRCODE1] = "\x00"

		self.reply[self.SMB_FLAG] = '\x80'
		self.reply[self.SMB_FLAG0] = "\x00"
		self.reply[self.SMB_FLAG1] = "\x01"
		
		self.reply[self.SMB_TREEID0] = "\x00"
		self.reply[self.SMB_TREEID1] = "\x08"

		self.reply[self.SMB_PID0] = message[self.SMB_PID0]
		self.reply[self.SMB_PID1] = message[self.SMB_PID1]

		self.reply[self.SMB_UID0] = "\x01"
		self.reply[self.SMB_UID1] = "\x08"

		self.reply[self.SMB_MID0] = message[self.SMB_MID0]
		self.reply[self.SMB_MID1] = message[self.SMB_MID1]
	
		fill = ['\x00'] * 96
		self.reply.extend(fill)

		### word count
		self.reply[36] = '\x0a'
		### totalparametercount
		self.reply[37] = '\x00'
		self.reply[38] = '\x00'
		### totaldatacount
		self.reply[39] = '\x48'
		self.reply[40] = '\x00'
		## reserved1 must be zero
		self.reply[41] = '\x00'
		self.reply[42] = '\x00'
		### parametercount - one transaction then equal to totalparametercount
		self.reply[43] = '\x00'
		self.reply[44] = '\x00'
		### parameteroffset bytes to transactionparameterbytes (parameters)
		self.reply[45] = '\x38'
		self.reply[46] = '\x00'
		### parameterdisplacement
		self.reply[47] = '\x00'
		self.reply[48] = '\x00'
		### DataCount -one transaction then equal to totaldatacount
		self.reply[49] = '\x48'
		self.reply[50] = '\x00'
		### DataOffset bytes to data
		self.reply[51] = '\x38'
		self.reply[52] = '\x00'
		### DataDisplacement
		self.reply[53] = '\x00'
		self.reply[54] = '\x00'
		### SetupCount
		self.reply[55] = '\x00'
		### reserved2
		self.reply[56] = '\x00'
		### byte count
		self.reply[57] = '\x49'
		self.reply[58] = '\x00'
		### padding
		self.reply[59] = '\x48'
		### dcerp version
		self.reply[60] = '\x05'
		### dcerp version minor
		self.reply[61] = '\x00'
		### packet type - ack
		self.reply[62] = '\x0c'
		### packet flags
		self.reply[63] = '\x03'
		### data representation
		self.reply[64] = '\x10'
		self.reply[65] = '\x00'
		self.reply[66] = '\x00'
		self.reply[67] = '\x00'
		### frag length
		self.reply[68] = '\x48'
		self.reply[69] = '\x00'
		### auth length
		self.reply[70] = '\x00'
		self.reply[71] = '\x00'
		### call id
		self.reply[72] = '\x01'
		self.reply[73] = '\x00'
		self.reply[74] = '\x00'
		self.reply[75] = '\x00'
		### max xmit frag
		self.reply[76] = '\xb8'
		self.reply[77] = '\x10'
		### max recv frag
		self.reply[78] = '\xb8'
		self.reply[79] = '\x10'
		### assoc group
		self.reply[80] = '\xa2'
		self.reply[81] = '\x55'
		self.reply[82] = '\x00'
		self.reply[83] = '\x00'
		### sec addr len
		self.reply[84] = '\x0f'
		self.reply[85] = '\x00'
		### sec addr
		self.reply[86] = '\x5c'
		self.reply[87] = '\x70'
		self.reply[88] = '\x69'
		self.reply[89] = '\x70'
		self.reply[90] = '\x65'
		self.reply[91] = '\x5c'
		self.reply[92] = '\x65'
		self.reply[93] = '\x70'
		self.reply[94] = '\x6d'
		self.reply[95] = '\x61'
		self.reply[96] = '\x70'
		self.reply[97] = '\x70'
		self.reply[98] = '\x65'
		self.reply[99] = '\x72'
		self.reply[100] = '\x00'
		###
		self.reply[101] = '\x00'
		self.reply[102] = '\x00'
		self.reply[103] = '\x00'
		### num results
		self.reply[104] = '\x01'
		###
		self.reply[105] = '\x00'
		self.reply[106] = '\x00'
		self.reply[107] = '\x00'
		
		### context
		self.reply[108] = '\x00'
		self.reply[109] = '\x00'
		self.reply[110] = '\x00'
		self.reply[111] = '\x00'
		self.reply[112] = '\x04'
		self.reply[113] = '\x5d'
		self.reply[114] = '\x88'
		self.reply[115] = '\x8a'
		self.reply[116] = '\xeb'
		self.reply[117] = '\x1c'
		self.reply[118] = '\xc9'
		self.reply[119] = '\x11'
		self.reply[120] = '\x9f'
		self.reply[121] = '\xe8'
		self.reply[122] = '\x08'
		self.reply[123] = '\x00'
		self.reply[124] = '\x2b'
		self.reply[125] = '\x10'
		self.reply[126] = '\x48'
		self.reply[127] = '\x60'
		self.reply[128] = '\x02'
		self.reply[129] = '\x00'
		self.reply[130] = '\x00'
		self.reply[131] = '\x00'

		###
		pktlength = struct.pack('!H', (len(self.reply)-4))
		self.reply[2:4] = pktlength
		return

	def smbLookUpReq(self, message, ownIP):
		self.reply = []
		self.reply.extend(list(self.net_header))
		self.reply.extend(list(self.smb_header))
		
		self.reply[self.SMB_COMMAND] = "\x25"

		self.reply[self.SMB_ERRCLASS] = "\x00"
		self.reply[self.SMB_ERRCODE1] = "\x00"

		self.reply[self.SMB_FLAG] = '\x80'
		self.reply[self.SMB_FLAG0] = "\x00"
		self.reply[self.SMB_FLAG1] = "\x01"
		
		self.reply[self.SMB_TREEID0] = "\x00"
		self.reply[self.SMB_TREEID1] = "\x08"

		self.reply[self.SMB_PID0] = message[self.SMB_PID0]
		self.reply[self.SMB_PID1] = message[self.SMB_PID1]

		self.reply[self.SMB_UID0] = "\x01"
		self.reply[self.SMB_UID1] = "\x08"

		self.reply[self.SMB_MID0] = message[self.SMB_MID0]
		self.reply[self.SMB_MID1] = message[self.SMB_MID1]
	
		fill = ['\x00'] * 220
		self.reply.extend(fill)

		### word count
		self.reply[36] = '\x0a'
		### totalparametercount
		self.reply[37] = '\x00'
		self.reply[38] = '\x00'
		### totaldatacount
		self.reply[39] = '\xc4'
		self.reply[40] = '\x00'
		## reserved1 must be zero
		self.reply[41] = '\x00'
		self.reply[42] = '\x00'
		### parametercount - one transaction then equal to totalparametercount
		self.reply[43] = '\x00'
		self.reply[44] = '\x00'
		### parameteroffset bytes to transactionparameterbytes (parameters)
		self.reply[45] = '\x38'
		self.reply[46] = '\x00'
		### parameterdisplacement
		self.reply[47] = '\x00'
		self.reply[48] = '\x00'
		### DataCount -one transaction then equal to totaldatacount
		self.reply[49] = '\xc4'
		self.reply[50] = '\x00'
		### DataOffset bytes to data
		self.reply[51] = '\x38'
		self.reply[52] = '\x00'
		### DataDisplacement
		self.reply[53] = '\x00'
		self.reply[54] = '\x00'
		### SetupCount
		self.reply[55] = '\x00'
		### reserved2
		self.reply[56] = '\x00'
		### byte count
		self.reply[57] = '\xc5'
		self.reply[58] = '\x00'
		### padding
		self.reply[59] = '\x64'
		### dcerp version
		self.reply[60] = '\x05'
		### dcerp version minor
		self.reply[61] = '\x00'
		### packet type - ack
		self.reply[62] = '\x02'
		### packet flags
		self.reply[63] = '\x03'
		### data representation
		self.reply[64] = '\x10'
		self.reply[65] = '\x00'
		self.reply[66] = '\x00'
		self.reply[67] = '\x00'
		### frag length
		self.reply[68] = '\xc4'
		self.reply[69] = '\x00'
		### auth length
		self.reply[70] = '\x00'
		self.reply[71] = '\x00'
		### call id
		self.reply[72] = '\x01'
		self.reply[73] = '\x00'
		self.reply[74] = '\x00'
		self.reply[75] = '\x00'
		### alloc hint
		self.reply[76] = '\xac'
		self.reply[77] = '\x00'
		self.reply[78] = '\x00'
		self.reply[79] = '\x00'
		### context id
		self.reply[80] = '\x00'
		self.reply[81] = '\x00'
		### cancel count
		self.reply[82] = '\x00'
		### opnum
		self.reply[83] = '\x00'
		### handle
		self.reply[84] = '\x00'
		self.reply[85] = '\x00'
		self.reply[86] = '\x00'
		self.reply[87] = '\x00'
		self.reply[88] = '\xf4'
		self.reply[89] = '\xfa'
		self.reply[90] = '\xc5'
		self.reply[91] = '\x8a'
		self.reply[92] = '\xa7'
		self.reply[93] = '\x51'
		self.reply[94] = '\xde'
		self.reply[95] = '\x11'
		self.reply[96] = '\xa6'
		self.reply[97] = '\x8c'
		self.reply[98] = '\x00'
		self.reply[99] = '\x0c'
		self.reply[100] = '\x29'
		self.reply[101] = '\xe0'
		self.reply[102] = '\x69'
		self.reply[103] = '\x22'
		### num entries
		self.reply[104] = '\x01'
		self.reply[105] = '\x00'
		self.reply[106] = '\x00'
		self.reply[107] = '\x00'
		### max count
		self.reply[108] = '\x01'
		self.reply[109] = '\x00'
		self.reply[110] = '\x00'
		self.reply[111] = '\x00'
		### offset
		self.reply[112] = '\x00'
		self.reply[113] = '\x00'
		self.reply[114] = '\x00'
		self.reply[115] = '\x00'
		### actual count
		self.reply[116] = '\x01'
		self.reply[117] = '\x00'
		self.reply[118] = '\x00'
		self.reply[119] = '\x00'
		### object
		self.reply[120] = '\x00'
		self.reply[121] = '\x00'
		self.reply[122] = '\x00'
		self.reply[123] = '\x00'
		self.reply[124] = '\x00'
		self.reply[125] = '\x00'
		self.reply[126] = '\x00'
		self.reply[127] = '\x00'
		self.reply[128] = '\x00'
		self.reply[129] = '\x00'
		self.reply[130] = '\x00'
		self.reply[131] = '\x00'
		self.reply[132] = '\x00'
		self.reply[133] = '\x00'
		self.reply[134] = '\x00'
		self.reply[135] = '\x00'
		### reference id
		self.reply[136] = '\x03'
		self.reply[137] = '\x00'
		self.reply[138] = '\x00'
		self.reply[139] = '\x00'
		### annotation offset
		self.reply[140] = '\x00'
		self.reply[141] = '\x00'
		self.reply[142] = '\x00'
		self.reply[143] = '\x00'
		### annotation length
		self.reply[144] = '\x12'
		self.reply[145] = '\x00'
		self.reply[146] = '\x00'
		self.reply[147] = '\x00'
		### annotation
		self.reply[148] = '\x4d'
		self.reply[149] = '\x65'
		self.reply[150] = '\x73'
		self.reply[151] = '\x73'
		self.reply[152] = '\x65'
		self.reply[153] = '\x6e'
		self.reply[154] = '\x67'
		self.reply[155] = '\x65'
		self.reply[156] = '\x72'
		self.reply[157] = '\x20'
		self.reply[158] = '\x53'
		self.reply[159] = '\x65'
		self.reply[160] = '\x72'
		self.reply[161] = '\x76'
		self.reply[162] = '\x69'
		self.reply[163] = '\x63'
		self.reply[164] = '\x65'
		self.reply[165] = '\x00'
		#### 
		self.reply[166] = '\x52'
		self.reply[167] = '\x8e'
		### length
		self.reply[168] = '\x4b'
		self.reply[169] = '\x00'
		self.reply[170] = '\x00'
		self.reply[171] = '\x00'
		### length
		self.reply[172] = '\x4b'
		self.reply[173] = '\x00'
		self.reply[174] = '\x00'
		self.reply[175] = '\x00'
		#### floors
		self.reply[176] = '\x05'
		self.reply[177] = '\x00'
		### lhs length
		self.reply[178] = '\x13'
		self.reply[179] = '\x00'
		### protocol
		self.reply[180] = '\x0d'
		### uuid
		### this is vuln 50 AB C2 A4 - 57 4D - 40 B3 - 9D 66- EE 4F D5 FB A0 76 (milworm)
		self.reply[181] = '\xa4'
		self.reply[182] = '\xc2'
		self.reply[183] = '\xab'
		self.reply[184] = '\x50'
		self.reply[185] = '\x4d'
		self.reply[186] = '\x57'
		self.reply[187] = '\xb3'
		self.reply[188] = '\x40'
		self.reply[189] = '\x9d'
		self.reply[190] = '\x66'
		self.reply[191] = '\xee'
		self.reply[192] = '\x4f'
		self.reply[193] = '\xd5'
		self.reply[194] = '\xfb'
		self.reply[195] = '\xa0'
		self.reply[196] = '\x76'
		### version
		self.reply[197] = '\x01'
		self.reply[198] = '\x00'
		### rhs length
		self.reply[199] = '\x02'
		self.reply[200] = '\x00'
		### version minor
		self.reply[201] = '\x00'
		self.reply[202] = '\x00'
		### lhs length
		self.reply[203] = '\x13'
		self.reply[204] = '\x00'
		### protocol
		self.reply[205] = '\x0d'
		### uuid
		self.reply[206] = '\x04'
		self.reply[207] = '\x5d'
		self.reply[208] = '\x88'
		self.reply[209] = '\x8a'
		self.reply[210] = '\xeb'
		self.reply[211] = '\x1c'
		self.reply[212] = '\xc9'
		self.reply[213] = '\x11'
		self.reply[214] = '\x9f'
		self.reply[215] = '\xe8'
		self.reply[216] = '\x08'
		self.reply[217] = '\x00'
		self.reply[218] = '\x2b'
		self.reply[219] = '\x10'
		self.reply[220] = '\x48'
		self.reply[221] = '\x60'
		### version
		self.reply[222] = '\x02'
		self.reply[223] = '\x00'
		### rhs length
		self.reply[224] = '\x02'
		self.reply[225] = '\x00'
		### version minor
		self.reply[226] = '\x00'
		self.reply[227] = '\x00'
		### lhs length
		self.reply[228] = '\x01'
		self.reply[229] = '\x00'
		### protocol
		self.reply[230] = '\x0a'
		### rhs length
		self.reply[231] = '\x02'
		self.reply[232] = '\x00'
		### version minor
		self.reply[233] = '\x00'
		self.reply[234] = '\x00'
		### lhs length
		self.reply[235] = '\x01'
		self.reply[236] = '\x00'
		### dod udp
		self.reply[237] = '\x08'
		### rhs length
		self.reply[238] = '\x02'
		self.reply[239] = '\x00'
		### udp port
		self.reply[240] = '\x00'
		self.reply[241] = '\x8b'
		### lhs length
		self.reply[242] = '\x01'
		self.reply[243] = '\x00'
		### dod ip
		self.reply[244] = '\x09'
		### rhs length
		self.reply[245] = '\x04'
		self.reply[246] = '\x00'
		### IP - 
		self.reply[247] = '\x00'
		self.reply[248] = '\x00'
		self.reply[249] = '\x00'
		self.reply[250] = '\x00'
		####
		self.reply[251] = '\x00'
		self.reply[252] = '\x00'
		self.reply[253] = '\x00'
		self.reply[254] = '\x00'
		self.reply[255] = '\x00'

		###
		iprepr = socket.inet_aton(ownIP)
		self.reply[248:252] = iprepr

		###
		pktlength = struct.pack('!H', (len(self.reply)-4))
		self.reply[2:4] = pktlength
		return

	def smbWriteAndX(self, message):
		self.reply = []
		self.reply.extend(list(self.net_header))
		self.reply.extend(list(self.smb_header))
		
		self.reply[self.SMB_COMMAND] = "\x2f"

		self.reply[self.SMB_ERRCLASS] = "\x00"
		self.reply[self.SMB_ERRCODE1] = "\x00"

		self.reply[self.SMB_FLAG] = '\x98'
		self.reply[self.SMB_FLAG0] = "\x01"
		self.reply[self.SMB_FLAG1] = "\x20"
		
		self.reply[self.SMB_TREEID0] = "\x00"
		self.reply[self.SMB_TREEID1] = "\x08"

		self.reply[self.SMB_PID0] = message[self.SMB_PID0]
		self.reply[self.SMB_PID1] = message[self.SMB_PID1]

		self.reply[self.SMB_UID0] = "\x01"
		self.reply[self.SMB_UID1] = "\x08"

		self.reply[self.SMB_MID0] = message[self.SMB_MID0]
		self.reply[self.SMB_MID1] = message[self.SMB_MID1]
		 
		fill = ['\x00'] * 15
		self.reply.extend(fill)

		### word count
		self.reply[36] = '\x06'
		### andx command
		self.reply[37] = '\xff'
		### andx reserved
		self.reply[38] = '\x00'
		### andx offset
		self.reply[39] = '\x2f'
		self.reply[40] = '\x00'
		### count
		self.reply[41] = message[36+21]
		self.reply[42] = message[36+22]
		### remaining
		self.reply[43] = '\xff'
		self.reply[44] = '\xff'
		### reserved
		self.reply[45] = '\x00'
		self.reply[46] = '\x00'
		self.reply[47] = '\x00'
		self.reply[48] = '\x00'
		### byte count
		self.reply[49] = '\x00'
		self.reply[50] = '\x00'
		###
		#print self.setCountItems
		if self.setCountItems == 1:
			self.NUM_COUNT_ITEMS = message[91]
			self.setCountItems = 0	
		pktlength = struct.pack('!H', (len(self.reply)-4))
		self.reply[2:4] = pktlength
		return

	def smbReadAndX(self, message):
		self.reply = []
		self.reply.extend(list(self.net_header))
		self.reply.extend(list(self.smb_header))
		
		self.reply[self.SMB_COMMAND] = "\x2e"

		self.reply[self.SMB_ERRCLASS] = "\x00"
		self.reply[self.SMB_ERRCODE1] = "\x00"

		self.reply[self.SMB_FLAG] = '\x98'
		self.reply[self.SMB_FLAG0] = "\x01"
		self.reply[self.SMB_FLAG1] = "\x20"
		
		self.reply[self.SMB_TREEID0] = "\x00"
		self.reply[self.SMB_TREEID1] = "\x08"

		self.reply[self.SMB_PID0] = message[self.SMB_PID0]
		self.reply[self.SMB_PID1] = message[self.SMB_PID1]

		self.reply[self.SMB_UID0] = "\x01"
		self.reply[self.SMB_UID1] = "\x08"
		self.reply[self.SMB_MID0] = message[self.SMB_MID0]
		self.reply[self.SMB_MID1] = message[self.SMB_MID1]
	
		fill = ['\x00'] * 72
		self.reply.extend(fill)

		### word count
		self.reply[36] = '\x0c'
		### andx command
		self.reply[37] = '\xff'
		### andx reserved
		self.reply[38] = '\x00'
		### andx offset
		self.reply[39] = '\x00'
		self.reply[40] = '\x00'
		### remaining
		self.reply[41] = '\x00'
		self.reply[42] = '\x00'
		### data compation mode
		self.reply[43] = '\x00'
		self.reply[44] = '\x00'
		### reserved
		self.reply[45] = '\x00'
		self.reply[46] = '\x00'
		### data length
		self.num = ord(self.NUM_COUNT_ITEMS)
		datalength = struct.pack('H', (44 + (self.num*24)))
		self.reply[47:49] = datalength
		#self.reply[47] = message[36+11]
		#self.reply[48] = message[36+12]
		### data offset
		self.reply[49] = '\x3c'
		self.reply[50] = '\x00'
		### reserved2
		self.reply[51] = '\x00'
		self.reply[52] = '\x00'
		### reserved3
		self.reply[53] = '\x00'
		self.reply[54] = '\x00'
		self.reply[55] = '\x00'
		self.reply[56] = '\x00'
		self.reply[57] = '\x00'
		self.reply[58] = '\x00'
		self.reply[59] = '\x00'
		self.reply[60] = '\x00'
		### byte count
		self.reply[61] = '\xad'
		self.reply[62] = '\x01'
		### padding
		self.reply[63] = '\x00'
		### DCERPC Data
		self.reply[64] = '\x05'
		self.reply[65] = '\x00'
		self.reply[66] = '\x0c'
		self.reply[67] = '\x03'
		self.reply[68] = '\x10'
		self.reply[69] = '\x00'
		self.reply[70] = '\x00'
		self.reply[71] = '\x00'
		self.reply[72:74] = datalength
		self.reply[74] = '\x00'
		self.reply[75] = '\x00'
		self.reply[76] = '\x00'
		self.reply[77] = '\x00'
		self.reply[78] = '\x00'
		self.reply[79] = '\x00'
		self.reply[80] = '\xb8'
		self.reply[81] = '\x10'
		self.reply[82] = '\xb8'
		self.reply[83] = '\x10'
		self.reply[84] = '\x7f'
		self.reply[85] = '\x28'
		self.reply[86] = '\x00'
		self.reply[87] = '\x00'
		self.reply[88] = '\x0e'
		self.reply[89] = '\x00'
		self.reply[90] = '\x5c'
		self.reply[91] = '\x50'
		self.reply[92] = '\x49'
		self.reply[93] = '\x50'
		self.reply[94] = '\x45'
		self.reply[95] = '\x5c'
		self.reply[96] = '\x62'
		self.reply[97] = '\x72'
		self.reply[98] = '\x6f'
		self.reply[99] = '\x77'
		self.reply[100] = '\x73'
		self.reply[101] = '\x65'
		self.reply[102] = '\x72'
		self.reply[103] = '\x00'
		###CTX_Items Anzahl
		self.reply[104] = self.NUM_COUNT_ITEMS
		self.reply[105] = '\x00'
		self.reply[106] = '\x00'
		self.reply[107] = '\x00'
		for i in range(self.num,1,-1):
			self.reply.extend(list(self.read_data_contextitem))
		self.reply.extend(list(self.read_last_data_contextitem)) 
		
		#print (len(self.reply)-63)
		bcc = struct.pack('H', (45 + (self.num*24)))
		self.reply[61:63] = bcc
		pktlength = struct.pack('!H', (len(self.reply)-4))
		self.reply[2:4] = pktlength
		return

	def consume(self, data, ownIP):
		if len(data)<10:
			return None
		### check for netbios session request packet
		if self.checkForNetbiosSessionRequest(data):
			#print ">> received netbios session request"
			self.NetbiosSessionReply(data)
			return "".join(self.reply)
		elif self.checkForNetbiosSessionRetargetRequest(data):
			print ">> received netbios session retarget request"
			self.NetbiosRetargetReply(data, ownIP)
			return "".join(self.reply)
		### check smb packet
		if self.checkForSMBPacket(data):
			commandByte = data[8]
			if commandByte == '\x72':
				#print ">> received smb negotiate request"
				dialectIndex = self.getsmbNegotInfo(data)
				self.smbNegotReply(data, dialectIndex)
				return "".join(self.reply)
			elif commandByte == '\x73':
				#print ">> received session setup andX request"
				self.smbSessionAndXReply(data)
				return "".join(self.reply)
			elif commandByte == '\x75':
				#print ">> received tree connect andX request"
				self.smbTreeConnectReply(data)
				return "".join(self.reply)
			elif commandByte == '\xa2':
				#print ">> received nt create andX request"
				self.smbNTCreateReply(data)
				return "".join(self.reply)
			elif commandByte == '\x25':
				try:
					packetType = data[self.SMB_PACKETTYPE]
				except:
					packetType = 'Not found'
				if packetType == '\x0b':
					#print ">> received smb transaction bind request"
					#self.examineTransaction(data)
					self.smbTransaction(data)
					return "".join(self.reply)
				elif packetType == '\x00':
					#print ">> received smb lookup request"
					self.smbLookUpReq(data, ownIP)
					return "".join(self.reply)
				else:
					print ">> Unknown SMB Packet Type Request: %s" % ([packetType])
					print ">> %s" % ([data])
					return None
			elif commandByte == '\x2f':
				#print ">> received smb write andx request"
				#fh = open("res.hex", 'a+')
				#fh.write(data)
				#fh.close()
				self.smbWriteAndX(data)
				return "".join(self.reply)
			elif commandByte == '\x2e':
				#print ">> received smb read andx request"
				self.smbReadAndX(data)
				return "".join(self.reply)
			elif commandByte == '\x71':
				#print ">> received end connection request"
				return None
			else:
				print ">> Unknown SMB Request: %s" % (commandByte)
				return None
		else:
			#print ">> no answer"
			return None
		


if __name__ == '__main__':
	print "simple smb server"
	try:
		port = int(sys.argv[1])
	except:
		port = 139
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(("127.0.0.1", port))
	s.listen(2)

	conn, addr = s.accept()

	print 'Connected by', addr

	smb = smbProt()

	while 1:
		data = conn.recv(4096)
		if not data:
			break
		print [data]
		smb.print_message(data)
		reply = smb.consume(data)
		#print [reply]
		#smb.print_message(reply)
		#reply = reply+"\r\n"
		if reply!=None and len(reply)>0:
			bytestosend = len(reply)
			print "sending %s bytes" % (bytestosend)
			bsent = conn.sendall(reply)
	
	#conn, addr = s.accept()
	#print 'Connected by', addr
	#smb = smbProt()

	#while 1:
	#	data = conn.recv(4096)
	#	if not data:
	#		break
	#	print [data]
	#	reply = smb.consume(data)
	#	if reply!=None and len(reply)>0:
	#		bytestosend = len(reply)
	#		print "sending %s bytes" % (bytestosend)
	#		bsent = conn.sendall(reply)
	#	else:
	#		bsent = conn.sendall('OK')
	s.close()
