# Copyright (c) 2017 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import pyqtSignal, pyqtProperty, QObject, QVariant, pyqtSlot
from UM.Logger import Logger

from typing import Optional

MYPY = False
if MYPY:
    from cura.PrinterOutput.PrinterOutputModel import PrinterOutputModel
    from cura.PrinterOutput.MaterialOutputModel import MaterialOutputModel


class ExtruderOutputModel(QObject):
    hotendIDChanged = pyqtSignal()
    targetHotendTemperatureChanged = pyqtSignal()
    hotendTemperatureChanged = pyqtSignal()
    activeMaterialChanged = pyqtSignal()
    isPreheatingChanged = pyqtSignal()

    def __init__(self, printer: "PrinterOutputModel", position: int, parent=None):
        super().__init__(parent)
        self._printer = printer
        self._position = position
        self._target_hotend_temperature = 0
        self._hotend_temperature = 0
        self._hotend_id = ""
        self._active_material = None  # type: Optional[MaterialOutputModel]
        self._is_preheating = False

    def getPrinter(self):
        return self._printer

    def getPosition(self):
        return self._position

    @pyqtProperty(QObject, notify = activeMaterialChanged)
    def activeMaterial(self) -> "MaterialOutputModel":
        return self._active_material

    def updateActiveMaterial(self, material: Optional["MaterialOutputModel"]):
        if self._active_material != material:
            self._active_material = material
            self.activeMaterialChanged.emit()

    ##  Update the hotend temperature. This only changes it locally.
    def updateHotendTemperature(self, temperature: float):
        if self._hotend_temperature != temperature:
            self._hotend_temperature = temperature
            self.hotendTemperatureChanged.emit()

    def updateTargetHotendTemperature(self, temperature: float):
        if self._target_hotend_temperature != temperature:
            self._target_hotend_temperature = temperature
            self.targetHotendTemperatureChanged.emit()

    ##  Set the target hotend temperature. This ensures that it's actually sent to the remote.
    @pyqtSlot(float)
    def setTargetHotendTemperature(self, temperature: float):
        self._printer.getController().setTargetHotendTemperature(self._printer, self, temperature)
        self.updateTargetHotendTemperature(temperature)

    @pyqtProperty(float, notify = targetHotendTemperatureChanged)
    def targetHotendTemperature(self) -> float:
        return self._target_hotend_temperature

    @pyqtProperty(float, notify=hotendTemperatureChanged)
    def hotendTemperature(self) -> float:
        return self._hotend_temperature

    @pyqtProperty(str, notify = hotendIDChanged)
    def hotendID(self) -> str:
        return self._hotend_id

    def updateHotendID(self, id: str):
        if self._hotend_id != id:
            self._hotend_id = id
            self.hotendIDChanged.emit()

    def updateIsPreheating(self, pre_heating):
        if self._is_preheating != pre_heating:
            self._is_preheating = pre_heating
            self.isPreheatingChanged.emit()

    @pyqtProperty(bool, notify=isPreheatingChanged)
    def isPreheating(self):
        return self._is_preheating

    ##  Pre-heats the extruder before printer.
    #
    #   \param temperature The temperature to heat the extruder to, in degrees
    #   Celsius.
    #   \param duration How long the bed should stay warm, in seconds.
    @pyqtSlot(float, float)
    def preheatHotend(self, temperature, duration):
        self._printer._controller.preheatHotend(self, temperature, duration)

    @pyqtSlot()
    def cancelPreheatHotend(self):
        self._printer._controller.cancelPreheatHotend(self)