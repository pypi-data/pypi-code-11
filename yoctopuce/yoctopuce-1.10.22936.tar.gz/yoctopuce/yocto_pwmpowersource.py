#*********************************************************************
#*
#* $Id: yocto_pwmpowersource.py 19610 2015-03-05 10:39:47Z seb $
#*
#* Implements yFindPwmPowerSource(), the high-level API for PwmPowerSource functions
#*
#* - - - - - - - - - License information: - - - - - - - - - 
#*
#*  Copyright (C) 2011 and beyond by Yoctopuce Sarl, Switzerland.
#*
#*  Yoctopuce Sarl (hereafter Licensor) grants to you a perpetual
#*  non-exclusive license to use, modify, copy and integrate this
#*  file into your software for the sole purpose of interfacing
#*  with Yoctopuce products.
#*
#*  You may reproduce and distribute copies of this file in
#*  source or object form, as long as the sole purpose of this
#*  code is to interface with Yoctopuce products. You must retain
#*  this notice in the distributed source file.
#*
#*  You should refer to Yoctopuce General Terms and Conditions
#*  for additional information regarding your rights and
#*  obligations.
#*
#*  THE SOFTWARE AND DOCUMENTATION ARE PROVIDED 'AS IS' WITHOUT
#*  WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING 
#*  WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, FITNESS
#*  FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO
#*  EVENT SHALL LICENSOR BE LIABLE FOR ANY INCIDENTAL, SPECIAL,
#*  INDIRECT OR CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA,
#*  COST OF PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY OR 
#*  SERVICES, ANY CLAIMS BY THIRD PARTIES (INCLUDING BUT NOT 
#*  LIMITED TO ANY DEFENSE THEREOF), ANY CLAIMS FOR INDEMNITY OR
#*  CONTRIBUTION, OR OTHER SIMILAR COSTS, WHETHER ASSERTED ON THE
#*  BASIS OF CONTRACT, TORT (INCLUDING NEGLIGENCE), BREACH OF
#*  WARRANTY, OR OTHERWISE.
#*
#*********************************************************************/


__docformat__ = 'restructuredtext en'
from yoctopuce.yocto_api import *


#--- (YPwmPowerSource class start)
#noinspection PyProtectedMember
class YPwmPowerSource(YFunction):
    """
    The Yoctopuce application programming interface allows you to configure
    the voltage source used by all PWM on the same device.

    """
#--- (end of YPwmPowerSource class start)
    #--- (YPwmPowerSource return codes)
    #--- (end of YPwmPowerSource return codes)
    #--- (YPwmPowerSource dlldef)
    #--- (end of YPwmPowerSource dlldef)
    #--- (YPwmPowerSource definitions)
    POWERMODE_USB_5V = 0
    POWERMODE_USB_3V = 1
    POWERMODE_EXT_V = 2
    POWERMODE_OPNDRN = 3
    POWERMODE_INVALID = -1
    #--- (end of YPwmPowerSource definitions)

    def __init__(self, func):
        super(YPwmPowerSource, self).__init__(func)
        self._className = 'PwmPowerSource'
        #--- (YPwmPowerSource attributes)
        self._callback = None
        self._powerMode = YPwmPowerSource.POWERMODE_INVALID
        #--- (end of YPwmPowerSource attributes)

    #--- (YPwmPowerSource implementation)
    def _parseAttr(self, member):
        if member.name == "powerMode":
            self._powerMode = member.ivalue
            return 1
        super(YPwmPowerSource, self)._parseAttr(member)

    def get_powerMode(self):
        """
        Returns the selected power source for the PWM on the same device

        @return a value among YPwmPowerSource.POWERMODE_USB_5V, YPwmPowerSource.POWERMODE_USB_3V,
        YPwmPowerSource.POWERMODE_EXT_V and YPwmPowerSource.POWERMODE_OPNDRN corresponding to the selected
        power source for the PWM on the same device

        On failure, throws an exception or returns YPwmPowerSource.POWERMODE_INVALID.
        """
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI.DefaultCacheValidity) != YAPI.SUCCESS:
                return YPwmPowerSource.POWERMODE_INVALID
        return self._powerMode

    def set_powerMode(self, newval):
        """
        Changes  the PWM power source. PWM can use isolated 5V from USB, isolated 3V from USB or
        voltage from an external power source. The PWM can also work in open drain  mode. In that
        mode, the PWM actively pulls the line down.
        Warning: this setting is common to all PWM on the same device. If you change that parameter,
        all PWM located on the same device are  affected.
        If you want the change to be kept after a device reboot, make sure  to call the matching
        module saveToFlash().

        @param newval : a value among YPwmPowerSource.POWERMODE_USB_5V, YPwmPowerSource.POWERMODE_USB_3V,
        YPwmPowerSource.POWERMODE_EXT_V and YPwmPowerSource.POWERMODE_OPNDRN corresponding to  the PWM power source

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("powerMode", rest_val)

    @staticmethod
    def FindPwmPowerSource(func):
        """
        Retrieves a voltage source for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the voltage source is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YPwmPowerSource.isOnline() to test if the voltage source is
        indeed online at a given time. In case of ambiguity when looking for
        a voltage source by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param func : a string that uniquely characterizes the voltage source

        @return a YPwmPowerSource object allowing you to drive the voltage source.
        """
        # obj
        obj = YFunction._FindFromCache("PwmPowerSource", func)
        if obj is None:
            obj = YPwmPowerSource(func)
            YFunction._AddToCache("PwmPowerSource", func, obj)
        return obj

    def nextPwmPowerSource(self):
        """
        Continues the enumeration of Voltage sources started using yFirstPwmPowerSource().

        @return a pointer to a YPwmPowerSource object, corresponding to
                a voltage source currently online, or a None pointer
                if there are no more Voltage sources to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YPwmPowerSource.FindPwmPowerSource(hwidRef.value)

#--- (end of YPwmPowerSource implementation)

#--- (PwmPowerSource functions)

    @staticmethod
    def FirstPwmPowerSource():
        """
        Starts the enumeration of Voltage sources currently accessible.
        Use the method YPwmPowerSource.nextPwmPowerSource() to iterate on
        next Voltage sources.

        @return a pointer to a YPwmPowerSource object, corresponding to
                the first source currently online, or a None pointer
                if there are none.
        """
        devRef = YRefParam()
        neededsizeRef = YRefParam()
        serialRef = YRefParam()
        funcIdRef = YRefParam()
        funcNameRef = YRefParam()
        funcValRef = YRefParam()
        errmsgRef = YRefParam()
        size = YAPI.C_INTSIZE
        #noinspection PyTypeChecker,PyCallingNonCallable
        p = (ctypes.c_int * 1)()
        err = YAPI.apiGetFunctionsByClass("PwmPowerSource", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YPwmPowerSource.FindPwmPowerSource(serialRef.value + "." + funcIdRef.value)

#--- (end of PwmPowerSource functions)
