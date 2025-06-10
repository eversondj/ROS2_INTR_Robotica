# ROS2_INTR_Robotica
# Waypoint Follower ROS 2

Este projeto implementa um nó ROS 2 em Python que controla o movimento de um robô por meio de uma sequência de waypoints. O nó utiliza a odometria recebida pelo tópico `/odom` e publica comandos de velocidade no tópico `/cmd_vel`.
#Link para o Video no Youtube

## 📦 Requisitos

- ROS 2 (Foxy, Galactic ou superior)
- Python 3.8+
- Pacotes:
  - `rclpy`
  - `geometry_msgs`
  - `nav_msgs`

## 🚀 Execução

### 1. Clone este repositório ou adicione o arquivo ao seu workspace

```bash
cd ~/ros2_ws/src
git clone <url-do-repositório>  # ou mova o arquivo manualmente
```

### 2. Estrutura esperada

```
robot_controller/
├── robot_controller_node.py
└── README.md
```

### 3. Configuração do pacote

Crie a estrutura de pacote ROS 2 com `ament_python`:

```bash
ros2 pkg create --build-type ament_python robot_controller
cd robot_controller
mkdir robot_controller
mv ../robot_controller_node.py robot_controller/
touch robot_controller/__init__.py
```

Edite o `setup.py`:

```python
from setuptools import setup

package_name = 'robot_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Seu Nome',
    maintainer_email='seu@email.com',
    description='Nó ROS 2 para seguir waypoints usando odometria.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'robot_controller_node = robot_controller.robot_controller_node:main',
        ],
    },
)
```

### 4. Compile o workspace

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

### 5. Execute o nó

```bash
ros2 run robot_controller robot_controller_node
```

Certifique-se de que os tópicos `/cmd_vel` e `/odom` estejam ativos no seu ambiente de simulação ou robô real.

## 🗺️ Sobre o funcionamento

O robô:
- Lê sua posição e orientação via `/odom`
- Calcula a direção e distância até o próximo waypoint
- Alinha-se e se move até o ponto
- Passa para o próximo ponto automaticamente

## 📎 Autor

Projeto para fins acadêmicos e de simulação.
