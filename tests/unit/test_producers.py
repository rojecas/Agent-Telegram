#!/usr/bin/env python3
"""
Test unitario para los productores del sistema Andrew Martin.
Verifica la implementación del Issue #18: Independencia de Canales (Productores) según SOLID.
"""

import sys
import os
import threading
import queue
import time
import unittest
from unittest.mock import Mock, patch, MagicMock

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.producers.base import BaseProducer
from src.core.producers.keyboard import KeyboardProducer
from src.core.producers.telegram import TelegramProducer
from src.core.models import Message

class TestBaseProducer(unittest.TestCase):
    """Test para la clase base BaseProducer."""
    
    def setUp(self):
        self.message_queue = queue.Queue()
        
        # Crear una implementación concreta para testear BaseProducer
        class ConcreteProducer(BaseProducer):
            def start(self):
                self.running = True
                
            def stop(self):
                self.running = False
                
        self.producer = ConcreteProducer(self.message_queue)
    
    def test_initialization(self):
        """Test de inicialización de BaseProducer."""
        self.assertEqual(self.producer.message_queue, self.message_queue)
        self.assertFalse(self.producer.running)
    
    def test_emit_message(self):
        """Test del método emit para enviar mensajes a la cola."""
        test_message = Message(
            priority=2,
            content="Test message",
            source="test",
            user_id="test_user",
            chat_id="test_chat"
        )
        
        self.producer.emit(test_message)
        
        # Verificar que el mensaje está en la cola
        self.assertFalse(self.message_queue.empty())
        queued_message = self.message_queue.get()
        self.assertEqual(queued_message.content, "Test message")
        self.assertEqual(queued_message.source, "test")
    
    def test_abstract_methods(self):
        """Test que verifica que BaseProducer es abstracta."""
        with self.assertRaises(TypeError):
            # No se puede instanciar BaseProducer directamente
            BaseProducer(self.message_queue)

class TestKeyboardProducer(unittest.TestCase):
    """Test para KeyboardProducer."""
    
    def setUp(self):
        self.message_queue = queue.Queue()
        self.producer = KeyboardProducer(self.message_queue)
    
    def test_initialization(self):
        """Test de inicialización de KeyboardProducer."""
        self.assertEqual(self.producer.message_queue, self.message_queue)
        self.assertFalse(self.producer.running)
        self.assertIsNone(self.producer.thread)
    
    def test_start_stop(self):
        """Test de métodos start y stop."""
        self.producer.start()
        self.assertTrue(self.producer.running)
        self.assertIsNotNone(self.producer.thread)
        self.assertTrue(self.producer.thread.daemon)
        
        self.producer.stop()
        self.assertFalse(self.producer.running)
    
    @patch('builtins.input', side_effect=["Hello", "exit"])
    def test_keyboard_input(self, mock_input):
        """Test de entrada de teclado simulada."""
        self.producer.start()
        
        # Esperar a que el hilo termine (procesará "Hello" y luego "exit")
        if self.producer.thread:
            self.producer.thread.join(timeout=1.0)
            
        # El hilo debería haberse detenido correctamente (por el "exit")
        self.assertFalse(self.producer.running)
        
        # Verificar que la cola tiene al menos un mensaje
        self.assertFalse(self.message_queue.empty())
        
        # Verificar que input fue llamado
        mock_input.assert_called()

class TestTelegramProducer(unittest.TestCase):
    """Test para TelegramProducer."""
    
    def setUp(self):
        self.message_queue = queue.Queue()
        self.producer = TelegramProducer(self.message_queue)
    
    def test_initialization(self):
        """Test de inicialización de TelegramProducer."""
        self.assertEqual(self.producer.message_queue, self.message_queue)
        self.assertFalse(self.producer.running)
        self.assertIsNone(self.producer.thread)
        self.assertEqual(self.producer.last_update_id, 0)
    
    def test_start_without_token(self):
        """Test de start sin token de Telegram."""
        with patch.dict(os.environ, {}, clear=True):
            self.producer.start()
            # Sin token, no debería iniciar
            self.assertFalse(self.producer.running)
    
    @patch('src.core.producers.telegram.telegram_receive')
    @patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token'})
    def test_telegram_polling(self, mock_telegram_receive):
        """Test de polling de Telegram simulado."""
        # Configurar mock para simular respuesta de Telegram
        mock_telegram_receive.return_value = {
            "success": True,
            "count": 1,
            "updates": [
                {
                    "update_id": 123,
                    "text": "Hello from Telegram",
                    "chat_id": "test_chat",
                    "from": "test_user"
                }
            ]
        }
        
        self.producer.start()
        self.assertTrue(self.producer.running)
        
        # Dar tiempo amplio para un ciclo de polling (0.5s para asegurar que el thread inicie)
        time.sleep(0.5)
        
        # Detener el productor
        self.producer.stop()
        
        # Verificar que telegram_receive fue llamado
        mock_telegram_receive.assert_called()
        
        # Verificar que last_update_id se actualizó
        self.assertEqual(self.producer.last_update_id, 123)

class TestProducerIntegration(unittest.TestCase):
    """Test de integración entre productores y cola de mensajes."""
    
    def test_multiple_producers_same_queue(self):
        """Test que verifica que múltiples productores pueden usar la misma cola."""
        message_queue = queue.PriorityQueue()
        
        # Crear productores (simulados)
        class MockProducer(BaseProducer):
            def __init__(self, message_queue, source_name):
                super().__init__(message_queue)
                self.source_name = source_name
                
            def start(self):
                self.running = True
                # Enviar un mensaje de prueba
                msg = Message(
                    priority=2,
                    content=f"Message from {self.source_name}",
                    source=self.source_name,
                    user_id="test_user",
                    chat_id="test_chat"
                )
                self.emit(msg)
                
            def stop(self):
                self.running = False
        
        # Crear múltiples productores
        producer1 = MockProducer(message_queue, "source1")
        producer2 = MockProducer(message_queue, "source2")
        
        # Iniciar productores
        producer1.start()
        producer2.start()
        
        # Verificar que hay mensajes en la cola
        self.assertEqual(message_queue.qsize(), 2)
        
        # Verificar contenido de los mensajes
        messages = []
        while not message_queue.empty():
            messages.append(message_queue.get())
        
        sources = [msg.source for msg in messages]
        self.assertIn("source1", sources)
        self.assertIn("source2", sources)

class TestSOLIDPrinciples(unittest.TestCase):
    """Test que verifica los principios SOLID en la implementación de productores."""
    
    def test_open_closed_principle(self):
        """Test del principio Open/Closed: sistema extensible sin modificar código existente."""
        # Crear un nuevo tipo de productor sin modificar BaseProducer
        class NewChannelProducer(BaseProducer):
            def start(self):
                self.running = True
                print("New channel started")
                
            def stop(self):
                self.running = False
        
        message_queue = queue.Queue()
        new_producer = NewChannelProducer(message_queue)
        
        # Verificar que se puede usar igual que otros productores
        self.assertIsInstance(new_producer, BaseProducer)
        new_producer.start()
        self.assertTrue(new_producer.running)
        
        # Verificar que puede emitir mensajes
        test_msg = Message(
            priority=2,
            content="Test from new channel",
            source="new_channel",
            user_id="user",
            chat_id="chat"
        )
        new_producer.emit(test_msg)
        
        self.assertFalse(message_queue.empty())
    
    def test_liskov_substitution(self):
        """Test del principio de Liskov: cualquier productor puede sustituir a BaseProducer."""
        producers = [
            KeyboardProducer(queue.Queue()),
            TelegramProducer(queue.Queue())
        ]
        
        for producer in producers:
            # Todos deben tener los métodos de BaseProducer
            self.assertTrue(hasattr(producer, 'start'))
            self.assertTrue(hasattr(producer, 'stop'))
            self.assertTrue(hasattr(producer, 'emit'))
            self.assertTrue(hasattr(producer, 'running'))
            
            # Todos deben poder emitir mensajes
            test_msg = Message(
                priority=2,
                content="Test",
                source="test",
                user_id="user",
                chat_id="chat"
            )
            producer.emit(test_msg)

if __name__ == '__main__':
    print("=== Ejecutando tests de productores ===")
    unittest.main(verbosity=2)
