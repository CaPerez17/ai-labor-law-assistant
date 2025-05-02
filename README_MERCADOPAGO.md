# Guía de Integración con MercadoPago

Esta guía explica cómo configurar y utilizar la integración con MercadoPago en LegalAssista para procesar pagos en modo sandbox.

## Requisitos Previos

1. Una cuenta en [MercadoPago Developers](https://developers.mercadopago.com/)
2. Acceso a las credenciales de prueba (Public Key y Access Token)

## Obtención de Credenciales

Para obtener las credenciales de MercadoPago:

1. Crea una cuenta o inicia sesión en [MercadoPago Developers](https://developers.mercadopago.com/)
2. Navega a la sección "Tus integraciones" o "Credenciales"
3. Selecciona el modo "Sandbox" para realizar pruebas
4. Copia las credenciales:
   - `Public Key`: Es la llave pública que se usa en el frontend
   - `Access Token`: Es la llave privada que se usa en el backend (¡nunca compartas esta información!)

## Configuración del Entorno

1. Abre el archivo `.env` en la raíz del proyecto
2. Agrega las siguientes variables de entorno:

```
MERCADOPAGO_PUBLIC_KEY=TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MERCADOPAGO_ACCESS_TOKEN=TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

3. Reemplaza los valores con tus credenciales de prueba

## Modo Sandbox vs Producción

### Modo Sandbox (Pruebas)

Las credenciales de sandbox están precedidas por `TEST-` y permiten realizar pruebas sin procesar pagos reales.

Para probar pagos en modo sandbox:

1. Usa las tarjetas de prueba proporcionadas por MercadoPago:
   - MASTERCARD: 5031 7557 3453 0604
   - VISA: 4509 9535 6623 3704
   - AMERICAN EXPRESS: 3711 803032 57522

2. Fecha de vencimiento: Cualquier fecha futura
3. CVV: Cualquier código de 3 o 4 dígitos
4. Nombre del titular: Cualquier nombre
5. DNI: Cualquier número válido

### Modo Producción

Para pasar a producción:

1. Completa el proceso de verificación en MercadoPago
2. Obtén credenciales de producción (sin el prefijo `TEST-`)
3. Actualiza las variables de entorno con las credenciales de producción

## Flujo de Pago

1. El usuario selecciona una factura pendiente y hace clic en "Pagar con MercadoPago"
2. El sistema crea una preferencia de pago en MercadoPago
3. El usuario es redirigido al checkout de MercadoPago
4. El usuario completa el pago
5. MercadoPago notifica al webhook de la aplicación sobre el resultado
6. La aplicación actualiza el estado de la factura según la respuesta

## Webhook de Notificaciones

MercadoPago enviará notificaciones de pago a:
```
http://[TU_DOMINIO]/api/v1/pagos/mercadopago/webhook
```

Para pruebas locales, puedes usar ngrok o herramientas similares para exponer tu servidor local a Internet y recibir las notificaciones.

## Solución de Problemas

### Los pagos no actualizan el estado de las facturas

1. Verifica que las credenciales de MercadoPago sean correctas
2. Asegúrate de que el webhook esté correctamente configurado y accesible
3. Revisa los logs del servidor para errores específicos

### Error de conexión a MercadoPago

1. Verifica tu conexión a Internet
2. Comprueba que las credenciales sean válidas
3. Asegúrate de estar utilizando la versión más reciente de la biblioteca de MercadoPago

### Otros problemas

Si encuentras otros problemas, consulta la [documentación oficial de MercadoPago](https://www.mercadopago.com.co/developers/es/docs/checkout-api/landing) o contacta al equipo de soporte de LegalAssista. 