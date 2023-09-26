# runtime.py
#
# Copyright 2022 brombinmirko <send@mirko.pm>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, in version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
from functools import lru_cache

from bottles.backend.globals import Paths


class RuntimeManager:

    @staticmethod
    @lru_cache
    def get_runtimes(_filter: str = "bottles"):
        runtimes = {
            "bottles": RuntimeManager.__get_bottles_runtime(),
            "steam": RuntimeManager.__get_steam_runtime()
        }

        if _filter == "steam":
            if len(runtimes.get("steam", {})) == 0:
                return False

        return runtimes.get(_filter, False)

    @staticmethod
    def get_runtime_env(_filter: str = "bottles", _append_ld: bool = False):
        runtime = RuntimeManager.get_runtimes(_filter)
        print("get_runtime_env runtime")
        print(runtime)
        env = ""

        if runtime:
            for p in runtime:
                if "EasyAntiCheatRuntime" in p or "BattlEyeRuntime" in p:
                    continue
                env += f"{p}:"
            env=env.removesuffix(":")
        else:
            return False
        print("get_runtime_env env")
        print(env)

        if _append_ld:
            ld = os.environ.get('LD_LIBRARY_PATH')
            if ld:
                env += f":{ld}"

        print("get_runtime_env env +ld")
        print(env)

        return env

    @staticmethod
    def get_eac():
        runtime = RuntimeManager.get_runtimes("bottles")

        if runtime:
            for p in runtime:
                if "EasyAntiCheatRuntime" in p:
                    return p

        return False

    @staticmethod
    def get_be():
        runtime = RuntimeManager.get_runtimes("bottles")

        if runtime:
            for p in runtime:
                if "BattlEyeRuntime" in p:
                    return p

        return False

    @staticmethod
    def __get_runtime(paths: list, structure: list):
        def check_structure(found, expected):
            print("found")
            print(found)
            print("expected")
            print(expected)
            for e in expected:
                if e not in found:
                    return False
            return True
        print("path: ")
        print(paths)
        print("structure: ")
        print(structure)
        for runtime_path in paths:
            if not os.path.exists(runtime_path):
                continue

            structure_found = []
            for dirs in structure:
                _path = os.path.join(runtime_path, dirs)
                if os.path.exists(_path):
                    structure_found.append(dirs)

            res = [f"{runtime_path}/{s}" for s in structure_found]
            eac_path = os.path.join(runtime_path, "EasyAntiCheatRuntime")
            be_path = os.path.join(runtime_path, "BattlEyeRuntime")

            if os.path.isdir(eac_path):
                res.append(eac_path)

            if os.path.isdir(be_path):
                res.append(be_path)
            
            print("__get_runtime: ")
            print(res)
            return res

        return []

    @staticmethod
    def __get_bottles_runtime():
        paths = [
            "/app/etc/runtime",
            Paths.runtimes
        ]
        structure = ["lib/x86_64-linux-gnu", "lib/i386-linux-gnu"]

        return RuntimeManager.__get_runtime(paths, structure)

    @staticmethod
    def __get_steam_runtime():
        from bottles.backend.managers.steam import SteamManager
        available_runtimes = {}
        steam_manager = SteamManager(check_only=True)

        if not steam_manager.is_steam_supported:
            return available_runtimes

        lookup = {
            "sniper": {
                "name": "sniper",
                "entry_point": os.path.join(steam_manager.steam_path, "steamapps/common/SteamLinuxRuntime_sniper/_v2-entry-point"),
            },
            "soldier": {
                "name": "soldier",
                "entry_point": os.path.join(steam_manager.steam_path, "steamapps/common/SteamLinuxRuntime_soldier/_v2-entry-point"),
            },
            "scout": {
                "name": "scout",
                "entry_point": os.path.join(steam_manager.steam_path, "ubuntu12_32/steam-runtime/run.sh"),
            }
        }

        for name, data in lookup.items():
            if not os.path.exists(data["entry_point"]):
                continue

            available_runtimes[name] = data

        return available_runtimes
