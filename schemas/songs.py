from marsh import  marsh
from models.songs import SongModel


class SongSchema(marsh.ModelSchema):
    class Meta:
        model = SongModel