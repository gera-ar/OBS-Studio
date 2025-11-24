# -*- coding: utf-8 -*-
# Copyright (C) 2025 Gerardo Kessler <gera.ar@yahoo.com>
# This file is covered by the GNU General Public License.

import appModuleHandler
from scriptHandler import script
import api
from time import sleep
import winUser
from ui import message
import speech
from threading import Thread
import addonHandler

# Lína de traducción
addonHandler.initTranslation()

# Función para romper la cadena de verbalización y callar al sintetizador durante el tiempo especificado
def mute(time, msg= False):
	if msg:
		message(msg)
		sleep(0.1)
	if speech.getState().speechMode == speech.SpeechMode.talk:
		def killSpeak(time):
			speech.setSpeechMode(speech.SpeechMode.off)
			sleep(time)
			speech.setSpeechMode(speech.SpeechMode.talk)
		Thread(target=killSpeak, args=(time,), daemon= True).start()

class AppModule(appModuleHandler.AppModule):

	category = "OBS Studio"

	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		self.fg = None
		self.status = None
		self.scenes = None
		self.sources = None
		self.controls = None
		self.audio_mixer = None
		self.recordButton = None
		# Translators: Mensaje de no encontrado
		self.notFound = _('Elemento no encontrado')

	def mouseClick(self, obj, mouse_button, text= None):
		buttons = {
			'left': [winUser.MOUSEEVENTF_LEFTDOWN, winUser.MOUSEEVENTF_LEFTUP],
			'right': [winUser.MOUSEEVENTF_RIGHTDOWN, winUser.MOUSEEVENTF_RIGHTUP]
		}
		api.moveMouseToNVDAObject(obj)
		if text: mute(0.2, obj.name)
		winUser.mouse_event(buttons[mouse_button][0],0,0,None,None)
		winUser.mouse_event(buttons[mouse_button][1],0,0,None,None)
		mute(0.3)

	def pressControl(self, id):
		if not self.controls: self.windowObjects()
		try:
			controls = self.controls.firstChild.firstChild.children
		except:
			return True
		for control in reversed(controls):
			if not hasattr(control, 'UIAAutomationId'): continue
			if control.UIAAutomationId == id:
				mute(0.5, control.name)
				control.doAction()
				return False
		return True

	def windowObjects(self):
		if not self.fg: self.fg = api.getForegroundObject()
		for child in self.fg.children:
			if not hasattr(child, 'UIAAutomationId'): continue
			if child.UIAAutomationId == 'OBSApp.OBSBasic.controlsDock': self.controls = child
			elif child.UIAAutomationId == 'OBSApp.OBSBasic.sourcesDock': self.sources = child
			elif child.UIAAutomationId == 'OBSApp.OBSBasic.statusbar': self.status = child
			elif child.UIAAutomationId == 'OBSApp.OBSBasic.scenesDock': self.scenes = child
			elif child.UIAAutomationId == 'OBSApp.OBSBasic.mixerDock': self.audio_mixer = child

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón Iniciar transmisión'),
		gesture="kb:control+t"
	)
	def script_transmision(self, gesture):
		if self.pressControl('OBSApp.OBSBasic.controlsDock.OBSBasicControls.controlsFrame.streamButton'):
			message(self.notFound)

	@script(
		category=category,
		#Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón Iniciar grabación'),
		gesture="kb:control+r"
	)
	def script_record(self, gesture):
		if self.pressControl('OBSApp.OBSBasic.controlsDock.OBSBasicControls.controlsFrame.recordButton'):
			message(self.notFound)

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón ajustes'),
		gesture="kb:control+a"
	)
	def script_settings(self, gesture):
		if self.pressControl('OBSApp.OBSBasic.controlsDock.OBSBasicControls.controlsFrame.settingsButton'):
			message(self.notFound)

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón pausar grabación'),
		gesture="kb:control+p"
	)
	def script_pausar(self, gesture):
		if self.pressControl('OBSApp.OBSBasic.controlsDock.OBSBasicControls.controlsFrame.pauseRecordButton'):
			# Translators: Mensaje sobre ninguna grabación en curso
			message(_('Ninguna grabación en curso'))

	@script(gestures=["kb:control+1","kb:control+2","kb:control+3"])
	def script_panelsFocus(self, gesture):
		x = int(gesture.mainKeyName)
		if not self.scenes: self.windowObjects()
		if x == 3 and self.controls:
			self.mouseClick(self.controls, 'right', True)
		elif x == 1 and self.scenes:
			self.mouseClick(self.scenes, 'left', True)
		elif x == 2 and self.sources:
			self.mouseClick(self.sources, 'left', True)

	@script(gestures=[f"kb:control+shift+{i}" for i in range(1, 10)])
	def script_mixerAudio(self, gesture):
		key = int(gesture.mainKeyName) - 1
		if not self.audio_mixer: self.windowObjects()
		try:
			obj = self.audio_mixer.firstChild.firstChild.firstChild.firstChild.firstChild.firstChild.children[key].firstChild
			mute(0.1, obj.next.name)
			obj.setFocus()
		except (AttributeError, IndexError):
			# Translators: Anuncia que no se han encontrado propiedades de audio
			message(_('Sin propiedades de audio'))

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Verbaliza el tiempo  grabado'),
		gesture="kb:control+shift+r"
	)
	def script_statusRecord(self, gesture):
		if not self.status: self.windowObjects()
		try:
			message(self.status.lastChild.getChild(3).lastChild.name)
		except AttributeError:
				pass

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Verbaliza el tiempo transmitido'),
		gesture="kb:control+shift+t"
	)
	def script_statusTransmission(self, gesture):
		if not self.status: self.windowObjects()
		try:
			message(self.status.lastChild.getChild(2).lastChild.name)
		except AttributeError:
			pass
