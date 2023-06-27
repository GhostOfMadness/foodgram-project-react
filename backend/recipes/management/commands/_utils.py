import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db.models import Model


DATA_FILES_DIR = Path(settings.BASE_DIR).parent
DATA_PATH = Path(DATA_FILES_DIR, 'data')


def upload_json_file(
        file_name: str,
        model: Model,
        exclude_fields: Tuple[str],
) -> Dict[str, List[str]]:
    """Read data, validate it and upload it to DB through Django ORM."""
    file_path = Path(DATA_PATH, file_name)
    with open(file_path, encoding='utf-8') as file_obj:
        total_count, valid_count = 0, 0
        model_objs: List[Any] = []
        errors: List[Dict[Any]] = []
        data_objects = json.load(file_obj)
        for data_object in data_objects:
            if 'image' in data_object.keys():
                path = Path(DATA_PATH, data_object['image'])
                data_object['image'] = File(
                    path.open(mode='rb'),
                    name=path.name,
                )
            total_count += 1
            obj = model(**data_object)
            try:
                obj.full_clean(exclude=exclude_fields)
                model_objs.append(obj)
                valid_count += 1
            except ValidationError as e:
                errors_dict = e.message_dict
                errors_dict['id'] = data_object['id']
                errors.append(errors_dict)
        model.objects.bulk_create(model_objs)
        return errors, total_count, valid_count
