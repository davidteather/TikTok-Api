from abc import abstractmethod
from typing import ClassVar, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from TikTokApi.tiktok import TikTokApi


class TikTokApiRoute:
    _parent: ClassVar["TikTokApi"]


class TikTokModel(BaseModel, TikTokApiRoute):
    raw_data: dict | None = Field(default_factory=dict, repr=False)

    @property
    def as_dict(self, **kwargs) -> dict:
        """
        Returns the model as a dictionary.

        """

        return self.model_dump(**kwargs)

    @abstractmethod
    def _extract_from_data(self, raw_data: dict):
        """
        Extracts relevant fields from the raw_data dictionary and assigns them to class attributes.

        """
        raise NotImplementedError("This method should be implemented by subclasses!")

    @classmethod
    def from_raw_data(cls, raw_data: dict):
        """
        Creates an instance of the class from raw data.

        Args:
            raw_data (dict): The raw data dictionary.

        Returns:
            An instance of the class.
        """

        instance = cls(raw_data=raw_data)
        instance._extract_from_data(raw_data)
        return instance

    def __repr__(self):
        return "TikTokApi." + super().__repr__()

    def __str__(self):
        return self.__repr__()
