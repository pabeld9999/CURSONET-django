from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Producto


class ListaProductosTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Programación")
        self.producto = Producto.objects.create(
            nombre="Python básico",
            precio=50,
            stock=10,
            activo=True,
            categoria=self.categoria,
        )

    def test_lista_muestra_categorias_y_cursos_al_seleccionar_una(self):
        response = self.client.get(reverse("lista_productos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Programación")
        self.assertNotContains(response, "Python básico")

        response = self.client.get(reverse("lista_productos_categoria", kwargs={"categoria_id": self.categoria.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Programación")
        self.assertContains(response, "Python básico")
