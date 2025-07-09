from util.logger import logger


class CancelManager:
    running_threads = []
    @staticmethod
    def add_running(thread_id):
        CancelManager.running_threads.append(thread_id)

    @staticmethod
    def remove_running(thread_id):
        if thread_id in CancelManager.running_threads:
            CancelManager.running_threads.remove(thread_id)

    @staticmethod
    def remove_all_running():
        if CancelManager.running_threads:
            logger.log('debug', f"canceled request thread_ids: {CancelManager.running_threads}")
            CancelManager.running_threads.clear()

    @staticmethod
    def check_running_state(thread_id):
        return thread_id in CancelManager.running_threads