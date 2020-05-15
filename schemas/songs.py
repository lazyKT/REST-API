from marsh import marsh
from models.songs import SongModel


class SongSchema(marsh.SQLAlchemySchema):
    class Meta:
        model = SongModel
        include_fk = True  # Include the foreign Key
