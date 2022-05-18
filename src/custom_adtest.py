import locale
from sys import stdin
import time
import re
from os.path import exists
from subprocess import run, PIPE, DEVNULL

from ruxit.api.base_plugin import BasePlugin
from ruxit.api.selectors import FromPluginSelector


# This extension uses the dsquery command to query AD for computer objects
# and capture the response time (secs) and return code as metrics
#
# When available the name of a specified domain controller is used as the
# metric deminsion
class ADTest(BasePlugin):

    def initialize(self, **kwargs):
        self.executions = 0

    # Uses the dsquery Micsosoft utility that is part of remote admin tools for AD
    # to capture the time to query AD

    def query(self, **kwargs):

        frequency = self.config.get("frequency", 1)
        self.logger.setLevel(self.config.get("log_level"))

        if self.executions % frequency == 0:
            self.logger.info(f"Running the ADTest plugin v1.024e")

            # Verify file exists before anything
            file_exists = exists('c:\windows\system32\dsquery.exe')
            if file_exists:
                self.logger.info(f"dsquery found")
            else:
                self.logger.warning(f"dsquery not found")
                raise Exception('required executable dsquery.exe not found')

            fullCmd = ['c:\windows\system32\dsquery.exe', 'computer']

            dimension = 'DC Not Specified'

            domainController = self.config["domainController"]
            useGC = self.config["useGC"]

            user = self.config["user"]
            password = self.config["password"]

            limit = self.config["limit"]

            if 'limit' in locals() and limit:
                if not type(limit) == "int":
                    limit = int(limit)

                if limit > 0:
                    fullCmd.append('-limit')

                    if limit > 1000:
                        fullCmd.append('1000')
                    else:
                        fullCmd.append(str(limit))

            # Use global catalog if useGC set to True
            if 'useGC' in locals() and useGC == True:
                fullCmd.append('-gc')
                dimension = 'Non Specific Global Catalog'
            # else use domain controller if is set
            # otherwise dsquery will just use what ever DC it wants
            else:
                if 'domainController' in locals() and domainController:
                    fullCmd.append('-s')
                    fullCmd.append(domainController)
                    dimension = domainController.upper()

            # Set the user and password
            if 'user' in locals() and user and 'password' in locals() and password:
                fullCmd.append('-u')
                fullCmd.append(user)
                fullCmd.append('-p')
                fullCmd.append(password)

            self.logger.info(fullCmd)

            startTime = time.time()

            # try:
            returnCode, errorMessage = self.cmd(fullCmd)
            stopTime = time.time()

            responseTime = stopTime - startTime
            self.logger.info(
                f'AD Test - Reporting metric value "{responseTime}"')
            self.logger.info(f'AD Test - Return Code "{returnCode}"')
            self.logger.info(
                f'AD Test 1.024e - Return Error Message "{errorMessage}"')

            returnCode, errorMessage = self.classifyError(errorMessage)

            if returnCode >= 3:
                raise Exception(errorMessage)

            self.results_builder.absolute(
                key='responseTime',
                value=responseTime,
                entity_selector=FromPluginSelector(),
                dimensions={'DomainController': dimension},
            )

            self.results_builder.absolute(
                key='returnCode',
                value=returnCode,
                entity_selector=FromPluginSelector(),
                dimensions={'DomainController': dimension},
            )

        self.executions += 1

    def classifyError(self, errorMsg):
        msgPosition = re.search('The logon attempt failed', errorMsg)
        if msgPosition:
            return 3, "Bad username or password"

        msgPosition = re.search('The server is not operational', errorMsg)
        if msgPosition:
            return 1, "Domain Controller invalid or not reachable"

        msgPosition = re.search(
            'reached the specified limit on number of results to display', errorMsg)
        if msgPosition:
            return 2, "Computer Limit Reached"

        return 0, " No message"

    def cmd(self, command):
        self.logger.info(f'ADTest - Attempting to execute: "{command}"')
        errorText = ""
        try:
            output = run(command, stdout=PIPE, shell=True,
                         stderr=PIPE, stdin=DEVNULL)
            self.logger.info(
                f"ADTest 1.024e - Try: {output} ({output.stdout})")
            errorText = output.stderr.decode()
        except:
            raise Exception(output.stderr.decode())

        return output.returncode, errorText