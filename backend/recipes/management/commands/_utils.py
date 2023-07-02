import json
from pathlib import Path
from typing import Any, ClassVar, Optional, Sequence

from django.conf import settings
from django.core.exceptions import (
    MultipleObjectsReturned,
    ObjectDoesNotExist,
    ValidationError,
)
from django.core.files import File
from django.db.models import Model


class JSONLoader:
    """
    Загрузка данных из json-файлов в базу данных.

    Параметры:
    - file_name - имя файла в директории data.
    - model - класс, объекты которого нужно создать.
    - exclude_fields - поля, которые должны быть исключены при валидации
    объекта (например, поле password для модели пользователя).
    - related_field_model_map - словарь из пар "имя зависимого поля - класс
    модели". Имя завимисого поля указывается в формате "имя класса модели
    в нижнем регистре_идентификатор объекта модели" (например, tag_slug).
    - file_fields - поля, содержащие ссылки на файлы в директории data.

    Файлы хранятся в директории data, которая расположена в корне проекта.
    """

    DATA_FILES_DIR: ClassVar[str] = settings.BASE_DIR
    DATA_PATH = Path(DATA_FILES_DIR, 'data')

    def __init__(
        self,
        file_name: str,
        model: Model,
        exclude_fields: Sequence[str] = (),
        related_field_model_map: dict[str, Model] = {},
        file_fields: Sequence[str] = (),
    ) -> None:
        self.file_name = file_name
        self.model = model
        self.exclude_fields = exclude_fields
        self.related_field_model_map = related_field_model_map
        self.file_fields = file_fields
        self.total_count = 0
        self.valid_count = 0
        self.errors = []
        self.model_objects = []

    def _data_object_repr(self, data_object: dict[str, Any]) -> str:
        """Преобразование словаря объекта в строку."""
        str_repr = ', '.join(
            [f'{key} - {value}' for key, value in data_object.items()],
        )
        return f'<{str_repr}>'

    def _error_field_handler(
        self,
        field: str,
        data_object: dict[str, Any],
        message: str,
    ) -> None:
        """Сохранение информации по ошибке поля в список self.errors."""
        str_repr = self._data_object_repr(data_object)
        error_dict = {
            'object': str_repr,
            'field': field,
            'error': message,
        }
        self.errors.append(error_dict)

    def _error_validation_handler(
        self,
        error: ValidationError,
        data_object: dict[str, Any],
    ):
        """Сохранение информации по ошибке валидации в список self.errors."""
        error_dict = error.message_dict
        error_dict['object'] = self._data_object_repr(data_object)
        self.errors.append(error_dict)

    def _file_handler(self, data_object: dict[str, Any]) -> dict[str, Any]:
        """Замена ссылки на файл его действительным представлением."""
        for field in self.file_fields:
            path = Path(self.DATA_PATH, data_object[field])
            data_object[field] = File(
                path.open(mode='rb'),
                name=path.name,
            )
        return data_object

    def _related_field_handler(
        self,
        data_object: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        """
        Замена идентификатора связанного объекта его первичным ключом.

        Метод возвращает None, если по идентификатору не удалось найти
        объект или было найдено несколько совпадений.
        """
        for field, model in self.related_field_model_map.items():
            field_name, search_param = field.split('_')
            model_field_name = f'{field_name}_id'
            params = {search_param: data_object[field]}
            try:
                data_object[model_field_name] = model.objects.get(**params).pk
                data_object.pop(field)
            except ObjectDoesNotExist:
                self._error_field_handler(
                    field=field,
                    data_object=data_object,
                    message='Объект не найден.',
                )
                data_object = None
                break
            except MultipleObjectsReturned:
                self._error_field_handler(
                    field=field,
                    data_object=data_object,
                    message='По данному полю найдено больше 1 совпадения.',
                )
                data_object = None
                break
        return data_object

    def create_model_objects(self) -> tuple[list[Any], int, int]:
        """Чтение, валидация и запись объектов в БД."""
        file_path = Path(self.DATA_PATH, self.file_name)
        with open(file_path, encoding='utf-8') as file_obj:
            data_objects = json.load(file_obj)
            for data_object in data_objects:
                self.total_count += 1
                data_object = self._file_handler(data_object)
                data_object = self._related_field_handler(data_object)
                try:
                    obj = self.model(**data_object)
                    obj.full_clean(exclude=self.exclude_fields)
                    self.model_objects.append(obj)
                    self.valid_count += 1
                except TypeError:
                    pass
                except ValidationError as e:
                    self._error_validation_handler(e, data_object)
        self.model.objects.bulk_create(self.model_objects)
        return self.errors, self.total_count, self.valid_count
