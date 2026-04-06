from __future__ import annotations

from pydantic import AliasChoices, BaseModel, Field


class NewPlainChunk(BaseModel):
    component_type: str = Field("page.plain-chunk", alias="__component")
    Header: str = Field(description="Header or subtitle for this chunk")
    Text: str = Field(description="The main text content, may include HTML markup")

    model_config = {
        "populate_by_name": True,
    }


class NewChunk(BaseModel):
    component_type: str = Field("page.chunk", alias="__component")
    Header: str = Field(description="Header or subtitle for this chunk")
    Text: str = Field(description="The main text content, may include HTML markup")
    KeyPhrase: str = Field(description="Key phrases for the chunk")
    Question: str = Field(description="Question for the chunk")
    Answer: str = Field(
        description="Answer for the chunk",
        validation_alias=AliasChoices("Answer", "ConstructedResponse"),
    )

    model_config = {
        "populate_by_name": True,
    }


class NewPage(BaseModel):
    Title: str = Field(description="The title of the page")
    Order: int = Field(description="The order of the page within the volume")
    ReferenceSummary: str = Field(description="A summary of the page")
    Content: list[NewChunk | NewPlainChunk] = Field(
        description="Array of content chunks within the page"
    )


class NewVolume(BaseModel):
    Title: str = Field(description="The title of the volume")
    Description: str = Field(description="The description of the volume")
    VolumeSummary: str = Field(description="A summary of the volume")
    Pages: list[NewPage] = Field(description="Array of pages within the volume")
