# import time
# from threading import Thread
#
# from utils import misc
#
# class ProcessListener:
#     def __init__(self):
#         self.listening = False
#
#         self.running = None
#
#         self.thread = None
#
#         self.interval = 5
#
#     @property
#     def running(self):
#         return self.running
#
#     @running.setter
#     def running(self, value):
#         print(value)
#         self.running = value
#
#     def start(self):
#         self.listening = True
#         self.thread = Thread(target=self._listening)
#         self.thread.start()
#         self.thread.join(self.interval)
#
#     def cancel(self):
#         self.listening = False
#         self.thread = None
#
#     def _listening(self):
#         if self.listening:
#             try:
#                 while True:
#                     if misc.check_if_process_is_running("LeagueClient"):
#                         print(0)
#                         if self.running is False:
#                             self.running = True
#                     else:
#                         print(1)
#                         if self.running is True:
#                             self.running = False
#                     time.sleep(self.interval)
#             except Exception as e:
#                 logger.debug(e)