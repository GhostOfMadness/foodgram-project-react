# Generated by Django 4.2.2 on 2023-07-04 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="recipe",
            old_name="ingredients",
            new_name="ingredient",
        ),
        migrations.RenameField(
            model_name="recipe",
            old_name="tags",
            new_name="tag",
        ),
        migrations.AlterField(
            model_name="recipeingredient",
            name="ingredient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipes",
                to="recipes.ingredient",
                verbose_name="Ингредиент",
            ),
        ),
        migrations.AlterField(
            model_name="recipeingredient",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredients",
                to="recipes.recipe",
                verbose_name="Рецепт",
            ),
        ),
        migrations.AlterField(
            model_name="recipetag",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tags",
                to="recipes.recipe",
                verbose_name="Рецепт",
            ),
        ),
        migrations.AlterField(
            model_name="recipetag",
            name="tag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipes",
                to="recipes.tag",
                verbose_name="Тег",
            ),
        ),
    ]
