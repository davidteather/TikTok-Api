import abc


class BrowserInterface(abc.ABC):
    @abc.abstractmethod
    def __init__(self, **kwargs):
        pass

    @abc.abstractmethod
    def get_params(self, page) -> None:
        pass

    # Returns verify_fp, device_id, signature, tt_params
    @abc.abstractmethod
    def sign_url(self, calc_tt_params=False, **kwargs):
        pass

    @abc.abstractmethod
    def _clean_up(self) -> None:
        pass
