# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import re
from typing import Tuple

class Version:
    def __init__(self, version_str: str):
        self.raw = str(version_str).strip()
        self.numbers: Tuple[int, ...] = ()
        self.suffix: str = ""
        self._parse()
    
    def _parse(self) -> None:
        if not self.raw:
            self.numbers = (0, 0, 0, 0)
            self.suffix = ""
            return
        
        ver = self.raw.lower()
        if ver.startswith('v'):
            ver = ver[1:]
        
        match = re.match(r'^(\d+(?:\.\d+)*)([a-z]*)$', ver)
        
        if not match:
            numbers = re.findall(r'\d+', ver)
            if numbers:
                nums = [int(n) for n in numbers]
                while len(nums) < 4:
                    nums.append(0)
                self.numbers = tuple(nums[:4])
                self.suffix = ""
            else:
                self.numbers = (0, 0, 0, 0)
                self.suffix = ""
            return
        
        num_part, suffix = match.groups()
        
        if '.' in num_part:
            nums = [int(n) for n in num_part.split('.')]
        else:
            nums = [int(num_part)]
        
        while len(nums) < 4:
            nums.append(0)
        
        self.numbers = tuple(nums[:4])
        self.suffix = suffix
    
    def _suffix_value(self) -> int:
        if not self.suffix:
            return 0
        
        value = 0
        for i, ch in enumerate(self.suffix):
            value = value * 27 + (ord(ch) - ord('a') + 1)
        return value
    
    def to_tuple(self) -> Tuple[int, ...]:
        return self.numbers + (self._suffix_value(),)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Version):
            return self.to_tuple() == other.to_tuple()
        try:
            return self.to_tuple() == Version(str(other)).to_tuple()
        except:
            return False
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __lt__(self, other) -> bool:
        if isinstance(other, Version):
            return self.to_tuple() < other.to_tuple()
        try:
            return self.to_tuple() < Version(str(other)).to_tuple()
        except:
            return False
    
    def __le__(self, other) -> bool:
        return self.__lt__(other) or self.__eq__(other)
    
    def __gt__(self, other) -> bool:
        return not self.__le__(other)
    
    def __ge__(self, other) -> bool:
        return not self.__lt__(other)
    
    def __str__(self) -> str:
        return self.raw
    
    def __repr__(self) -> str:
        return f"Version('{self.raw}')"
    
    @staticmethod
    def compare(ver1: str, ver2: str) -> int:
        v1 = Version(ver1)
        v2 = Version(ver2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    
    @staticmethod
    def is_newer(current: str, latest: str) -> bool:
        return Version.compare(current, latest) < 0

def compare_builds(current: str, latest: str) -> bool:
    return Version.is_newer(current, latest)

def compare_zapret_versions(current: str, latest: str) -> bool:
    return Version.is_newer(current, latest)

def version_to_tuple(ver_str: str) -> tuple:
    return Version(ver_str).to_tuple()

__all__ = [
    'Version',
    'compare_builds',
    'compare_zapret_versions',
    'version_to_tuple'
]