#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
#
# WeatherPlugin E2
#
# Coded by Dr.Best (c) 2012
# Support: www.dreambox-tools.info
# E-Mail: dr.best@dreambox-tools.info
#
# This plugin is open source but it is NOT free software.
#
# This plugin may only be distributed to and executed on hardware which
# is licensed by Dream Multimedia GmbH.
# In other words:
# It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
# to hardware which is NOT licensed by Dream Multimedia GmbH.
# It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
# on hardware which is NOT licensed by Dream Multimedia GmbH.
#
# If you want to use or modify the code or parts of it,
# you have to keep MY license and inform me about the modifications by mail.
#

# for localized messages
from . import _

from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_VALIGN_CENTER, getDesktop
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import ConfigSubsection, ConfigText, ConfigSelection, getConfigListEntry, config, configfile
from xml.etree.cElementTree import fromstring as cet_fromstring
from twisted.web.client import getPage
from urllib import quote as urllib_quote

from enigma import RT_HALIGN_RIGHT
from skin import parameters as skinparameter
from Screens.VirtualKeyBoard import VirtualKeyBoard

skinwidth = getDesktop(0).size().width()

def initWeatherPluginEntryConfig():
	s = ConfigSubsection()
	s.city = ConfigText(default = "Heidelberg", visible_width = 100, fixed_size = False)
	s.degreetype = ConfigSelection(choices = [("C", _("metric system")), ("F", _("imperial system"))], default = "C")
	s.weatherlocationcode = ConfigText(default = "", visible_width = 100, fixed_size = False)
	config.plugins.WeatherPlugin.Entry.append(s)
	return s

def initConfig():
	count = config.plugins.WeatherPlugin.entrycount.value
	if count != 0:
		i = 0
		while i < count:
			initWeatherPluginEntryConfig()
			i += 1

class MSNWeatherPluginEntriesListConfigScreen(Screen):
	if skinwidth == 1280:
	   skin = """
		<screen name="MSNWeatherPluginEntriesListConfigScreen" position="center,center" size="550,400">
			<widget render="Label" source="city" position="5,60" size="400,50" font="Regular;20" halign="left"/>
			<widget render="Label" source="degreetype" position="410,60" size="130,50" font="Regular;20" halign="left"/>
			<widget name="entrylist" position="0,80" size="550,300" scrollbarMode="showOnDemand"/>
			<widget render="Label" source="key_red" position="0,10" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<widget render="Label" source="key_green" position="140,10" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="green" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<widget render="Label" source="key_yellow" position="280,10" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="yellow" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<widget render="Label" source="key_blue" position="420,10" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<ePixmap position="0,10" zPosition="4" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap position="140,10" zPosition="4" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap position="280,10" zPosition="4" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on" />
			<ePixmap position="420,10" zPosition="4" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on" />
		</screen>"""
	else:
	   skin = """
		<screen name="MSNWeatherPluginEntriesListConfigScreen" position="center,center" size="811,508">
			<widget render="Label" source="city" position="5,70" size="400,50" font="Regular;35"/>
			<widget render="Label" source="degreetype" position="405,70" size="360,50" font="Regular;35"/>
			<widget name="entrylist" position="center,130" size="801,480" scrollbarMode="showOnDemand"/>
			<widget render="Label" source="key_red" position="5,5" size="200,60" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;30" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1"/>
			<widget render="Label" source="key_green" position="205,5" size="200,60" zPosition="5" valign="center" halign="center" backgroundColor="green" font="Regular;30" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1"/>
			<widget render="Label" source="key_yellow" position="405,5" size="200,60" zPosition="5" valign="center" halign="center" backgroundColor="yellow" font="Regular;30" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1"/>
			<widget render="Label" source="key_blue" position="605,5" zPosition="5" size="200,60" valign="center" halign="center" font="Regular;30" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1"/>
			<ePixmap position="30,10" zPosition="4" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on"/>
			<ePixmap position="230,10" zPosition="4" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on"/>
			<ePixmap position="430,10" zPosition="4" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="635,10" zPosition="4" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on"/>
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.title = _("WeatherPlugin: List of Entries")
		self["city"] = StaticText(_("City"))
		self["degreetype"] = StaticText(_("System"))
		self["key_red"] = StaticText(_("Back"))
		self["key_green"] = StaticText(_("Add"))		
		self["key_yellow"] = StaticText(_("Edit"))
		self["key_blue"] = StaticText(_("Delete"))
		self["entrylist"] = WeatherPluginEntryList([])
		self["actions"] = ActionMap(["WizardActions","MenuActions","ShortcutActions"],
			{
			 "ok"	:	self.keyOK,
			 "back"	:	self.keyClose,
			 "red"	:	self.keyClose,
			 "green":	self.keyGreen,			 
			 "yellow":	self.keyYellow,
			 "blue": 	self.keyDelete,
			 }, -1)
		self.updateList()

	def updateList(self):
		self["entrylist"].buildList()

	def keyClose(self):
		self.close(-1, None)

	def keyGreen(self):
		self.session.openWithCallback(self.updateList,MSNWeatherPluginEntryConfigScreen,None)

	def keyOK(self):
		try:sel = self["entrylist"].l.getCurrentSelection()[0]
		except: sel = None
		self.close(self["entrylist"].getCurrentIndex(), sel)

	def keyYellow(self):
		try:sel = self["entrylist"].l.getCurrentSelection()[0]
		except: sel = None
		if sel is None:
			return
		self.session.openWithCallback(self.updateList,MSNWeatherPluginEntryConfigScreen,sel)

	def keyDelete(self):
		try:sel = self["entrylist"].l.getCurrentSelection()[0]
		except: sel = None
		if sel is None:
			return
		self.session.openWithCallback(self.deleteConfirm, MessageBox, _("Really delete this WeatherPlugin Entry?"))

	def deleteConfirm(self, result):
		if not result:
			return
		sel = self["entrylist"].l.getCurrentSelection()[0]
		config.plugins.WeatherPlugin.entrycount.value -= 1
		config.plugins.WeatherPlugin.entrycount.save()
		config.plugins.WeatherPlugin.Entry.remove(sel)
		config.plugins.WeatherPlugin.Entry.save()
		config.plugins.WeatherPlugin.save()
		configfile.save()
		self.updateList()

class WeatherPluginEntryList(MenuList):
	def __init__(self, list, enableWrapAround = True):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		if skinwidth == 1280:
			font1, size1 = skinparameter.get("WeatherPluginEntryListFont1", ('Regular',20))
			font2, size2 = skinparameter.get("WeatherPluginEntryListFont2", ('Regular',18))
			self.l.setFont(0, gFont(font1, size1))
			self.l.setFont(1, gFont(font2, size2))
		else:
			font1, size1 = skinparameter.get("WeatherPluginEntryListFont1", ('Regular',28))
			font2, size2 = skinparameter.get("WeatherPluginEntryListFont2", ('Regular',26))
			self.l.setFont(0, gFont(font1, size1))
			self.l.setFont(1, gFont(font2, size2))

	def postWidgetCreate(self, instance):
		MenuList.postWidgetCreate(self, instance)
		if skinwidth == 1280:
		     instance.setItemHeight(25)
		else:
		     instance.setItemHeight(32)

	def getCurrentIndex(self):
		return self.instance.getCurrentIndex()

	def buildList(self):
		list = []
		for c in config.plugins.WeatherPlugin.Entry:
			if skinwidth == 1280:
				x1, y1, w1, h1 = skinparameter.get("WeatherPluginCity", (5, 0, 400, 20))
				x2, y2, w2, h2 = skinparameter.get("WeatherPluginDegreetype", (410, 0, 80, 20))
		    	else:
				x1, y1, w1, h1 = skinparameter.get("WeatherPluginCity", (5, 0, 400, 32))
				x2, y2, w2, h2 = skinparameter.get("WeatherPluginDegreetype", (410, 0, 80, 32))
			res = [
				c,
				(eListboxPythonMultiContent.TYPE_TEXT, x1, y1, w1, h1, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, str(c.city.value)),
				(eListboxPythonMultiContent.TYPE_TEXT, x2, y2, w2, h2, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, str(c.degreetype .value)),
			]
			list.append(res)
		self.list = list
		self.l.setList(list)
		self.moveToIndex(0)

class MSNWeatherPluginEntryConfigScreen(ConfigListScreen, Screen):
	if skinwidth == 1280:
	   skin = """
		<screen name="MSNWeatherPluginEntryConfigScreen" position="center,center" size="550,400">
			<widget name="config" position="20,60" size="520,300" scrollbarMode="showOnDemand" />
			<ePixmap position="0,10" zPosition="4" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap position="140,10" zPosition="4" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap position="420,10" zPosition="4" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on" />
			<ePixmap position="280,10" zPosition="4" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on" />
			<widget source="key_red" render="Label" position="0,10" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<widget source="key_green" render="Label" position="140,10" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<widget render="Label" source="key_yellow" position="280,10" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="yellow" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<widget source="key_blue" render="Label" position="420,10" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
		</screen>"""
	else:
	   skin = """
		<screen name="MSNWeatherPluginEntryConfigScreen" position="center,center" size="811,534">
			<widget name="config" position="8,75" size="794,450" scrollbarMode="showOnDemand"/>
			<ePixmap position="30,10" zPosition="4" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on"/>
			<ePixmap position="230,10" zPosition="4" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on"/>
			<ePixmap position="635,10" zPosition="4" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on"/>
			<ePixmap position="430,10" zPosition="4" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on"/>
			<widget source="key_red" render="Label" position="5,5" zPosition="5" size="200,60" valign="center" halign="center" font="Regular;30" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1"/>
			<widget source="key_green" render="Label" position="205,5" zPosition="5" size="200,60" valign="center" halign="center" font="Regular;30" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1"/>
			<widget render="Label" source="key_yellow" position="405,5" size="200,60" zPosition="5" valign="center" halign="center" backgroundColor="yellow" font="Regular;30" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1"/>
			<widget source="key_blue" render="Label" position="605,5" zPosition="5" size="200,60" valign="center" halign="center" font="Regular;30" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1"/>
		</screen>"""

	def __init__(self, session, entry):
		Screen.__init__(self, session)
		self.title = _("WeatherPlugin: Edit Entry")

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"green": self.keySave,
			"red": self.keyCancel,
			"blue": self.keyDelete,
			"yellow": self.searchLocation,
			"cancel": self.keyCancel,
			"ok": self.keyOK
		}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["key_blue"] = StaticText(_("Delete"))
		self["key_yellow"] = StaticText(_("Search Code"))

		if entry is None:
			self.newmode = 1
			self.current = initWeatherPluginEntryConfig()
		else:
			self.newmode = 0
			self.current = entry

		cfglist = [
			getConfigListEntry(_("City"), self.current.city),
			getConfigListEntry(_("Location code"), self.current.weatherlocationcode),
			getConfigListEntry(_("System"), self.current.degreetype)
		]

		ConfigListScreen.__init__(self, cfglist, session)
		
	def searchLocation(self):
		if self.current.city.value != "":
			language = config.osd.language.value.replace("_","-")
			if language == "en-EN": # hack
				language = "en-US"
			elif language == "no-NO": # hack
				language = "nn-NO"
			url = "http://weather.service.msn.com/find.aspx?src=outlook&outputview=search&weasearchstr=%s&culture=%s" % (urllib_quote(self.current.city.value), language)
			getPage(url).addCallback(self.xmlCallback).addErrback(self.error)
		else:
			self.session.open(MessageBox, _("You need to enter a valid city name before you can search for the location code."), MessageBox.TYPE_ERROR)

	def keySave(self):
		if self.current.city.value != "" and self.current.weatherlocationcode.value != "":
			if self.newmode == 1:
				config.plugins.WeatherPlugin.entrycount.value = config.plugins.WeatherPlugin.entrycount.value + 1
				config.plugins.WeatherPlugin.entrycount.save()
			ConfigListScreen.keySave(self)
			config.plugins.WeatherPlugin.save()
			configfile.save()
			self.close()
		else:
			if self.current.city.value == "":
				self.session.open(MessageBox, _("Please enter a valid city name."), MessageBox.TYPE_ERROR)
			else:
				self.session.open(MessageBox, _("Please enter a valid location code for the city."), MessageBox.TYPE_ERROR)

	def keyCancel(self):
		if self.newmode == 1:
			config.plugins.WeatherPlugin.Entry.remove(self.current)
		ConfigListScreen.cancelConfirm(self, True)

	def keyOK(self):
		text = self["config"].getCurrent()[1].value
		if text == self.current.city.value:
			title = _("Please enter a valid city name.")
			self.session.openWithCallback(self.VirtualKeyBoardCallBack, VirtualKeyBoard, title = title, text = text)
		elif text == self.current.weatherlocationcode.value:
			title = _("Please enter a valid location code for the city.")
			self.session.openWithCallback(self.VirtualKeyBoardCallBack, VirtualKeyBoard, title = title, text = text)
		else:
			pass

	def VirtualKeyBoardCallBack(self, callback):
		try:
			if callback:  
				self["config"].getCurrent()[1].value = callback
			else:
				pass
		except:
			pass

	def keyDelete(self):
		if self.newmode == 1:
			self.keyCancel()
		else:		
			self.session.openWithCallback(self.deleteConfirm, MessageBox, _("Really delete this WeatherPlugin Entry?"))

	def deleteConfirm(self, result):
		if not result:
			return
		config.plugins.WeatherPlugin.entrycount.value = config.plugins.WeatherPlugin.entrycount.value - 1
		config.plugins.WeatherPlugin.entrycount.save()
		config.plugins.WeatherPlugin.Entry.remove(self.current)
		config.plugins.WeatherPlugin.Entry.save()
		config.plugins.WeatherPlugin.save()
		configfile.save()
		self.close()

	def xmlCallback(self, xmlstring):
		if xmlstring:
			errormessage = ""
			root = cet_fromstring(xmlstring)
			for childs in root:
				if childs.tag == "weather" and childs.attrib.has_key("errormessage"):
					errormessage = childs.attrib.get("errormessage").encode("utf-8", 'ignore')
					break
			if len(errormessage) !=0:
				self.session.open(MessageBox, errormessage, MessageBox.TYPE_ERROR)					
			else:
				self.session.openWithCallback(self.searchCallback, MSNWeatherPluginSearch, xmlstring)
			
	def error(self, error = None):
		if error is not None:
			print(error)
		
	def searchCallback(self, result):
		if result:
			self.current.weatherlocationcode.value = result[0]
			self.current.city.value = result[1]

class MSNWeatherPluginSearch(Screen):
	if skinwidth == 1280:
	   skin = """
		<screen name="MSNWeatherPluginSearch" position="center,center" size="550,400">
			<widget name="entrylist" position="0,60" size="550,200" scrollbarMode="showOnDemand"/>
			<widget render="Label" source="key_red" position="0,10" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<widget render="Label" source="key_green" position="140,10" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="green" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<ePixmap position="0,10" zPosition="4" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap position="140,10" zPosition="4" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap position="280,10" zPosition="4" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on" />
			<ePixmap position="420,10" zPosition="4" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on" />
		</screen>"""
	else:
	   skin = """
		<screen name="MSNWeatherPluginSearch" position="center,center" size="811,534">
			<widget name="entrylist" position="center,70" size="800,457" scrollbarMode="showOnDemand"/>
			<widget render="Label" source="key_red" position="5,5" size="200,60" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1"/>
			<widget render="Label" source="key_green" position="205,5" size="200,60" zPosition="5" valign="center" halign="center" backgroundColor="green" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1"/>
			<ePixmap position="30,10" zPosition="4" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on"/>
			<ePixmap position="230,10" zPosition="4" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on"/>
			<ePixmap position="430,10" zPosition="4" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="635,10" zPosition="4" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on"/>
		</screen>"""

	def __init__(self, session, xmlstring):
		Screen.__init__(self, session)
		self.title = _("MSN location search result")
		self["key_red"] = StaticText(_("Back"))
		self["key_green"] = StaticText(_("OK"))		
		self["entrylist"] = MSNWeatherPluginSearchResultList([])
		self["actions"] = ActionMap(["WizardActions","MenuActions","ShortcutActions"],
		{
			"ok"   : self.keyOK,
			"green": self.keyOK,
			"back" : self.keyClose,
			"red"  : self.keyClose,
		}, -1)
		self.updateList(xmlstring)

	def updateList(self, xmlstring):
		self["entrylist"].buildList(xmlstring)

	def keyClose(self):
		self.close(None)

	def keyOK(self):
		pass
		try:sel = self["entrylist"].l.getCurrentSelection()[0]
		except: sel = None
		self.close(sel)

class MSNWeatherPluginSearchResultList(MenuList):
	def __init__(self, list, enableWrapAround = True):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		if skinwidth == 1280:
			font1, size1 = skinparameter.get("WeatherPluginSearchResultListFont1", ('Regular',20))
			font2, size2 = skinparameter.get("WeatherPluginSearchResultListFont2", ('Regular',18))
			self.l.setFont(0, gFont(font1, size1))
			self.l.setFont(1, gFont(font2, size2))
		else:
			font1, size1 = skinparameter.get("WeatherPluginSearchResultListFont1", ('Regular',28))
			font2, size2 = skinparameter.get("WeatherPluginSearchResultListFont2", ('Regular',26))
			self.l.setFont(0, gFont(font1, size1))
			self.l.setFont(1, gFont(font2, size2))

	def postWidgetCreate(self, instance):
		MenuList.postWidgetCreate(self, instance)
		if skinwidth == 1280:
		     instance.setItemHeight(44)
		else:
		     instance.setItemHeight(55)

	def getCurrentIndex(self):
		return self.instance.getCurrentIndex()

	def buildList(self, xml):
		root = cet_fromstring(xml)
		searchlocation = ""
		searchresult = ""
		weatherlocationcode = ""
		list = []
		for childs in root:
			if childs.tag == "weather":
				searchlocation = childs.attrib.get("weatherlocationname").encode("utf-8", 'ignore')
				searchresult = childs.attrib.get("weatherfullname").encode("utf-8", 'ignore')
				weatherlocationcode = childs.attrib.get("weatherlocationcode").encode("utf-8", 'ignore')
				if skinwidth == 1280:
					x1, y1, w1, h1 = skinparameter.get("WeatherPluginSearchlocation", (5, 0, 500, 20))
					x2, y2, w2, h2 = skinparameter.get("WeatherPluginSearchresult", (5, 22, 500, 20))
				else:
					x1, y1, w1, h1 = skinparameter.get("WeatherPluginSearchlocation", (5, 0, 500, 30))
					x2, y2, w2, h2 = skinparameter.get("WeatherPluginSearchresult", (5, 27, 500, 26))
					res = [
						(weatherlocationcode, searchlocation),
						(eListboxPythonMultiContent.TYPE_TEXT, x1, y1, w1, h1, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, searchlocation),
						(eListboxPythonMultiContent.TYPE_TEXT, x2, y2, w2, h2, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, searchresult),
					]

					list.append(res)
		self.list = list
		self.l.setList(list)
		self.moveToIndex(0)
