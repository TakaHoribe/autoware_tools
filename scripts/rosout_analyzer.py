import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import Log
from collections import defaultdict
import matplotlib.pyplot as plt
import argparse

class RosoutLogger(Node):
    def __init__(self, print_level):
        super().__init__('rosout_logger')
        self.log_counts = defaultdict(lambda: defaultdict(int))
        self.subscription = self.create_subscription(Log, '/rosout', self.rosout_callback, 10)
        self.timer = self.create_timer(1.0, self.print_summary)
        self.print_level = print_level

    def rosout_callback(self, msg):
        name_parts = msg.name.split('.')
        for i in range(len(name_parts)):
            namespace = '.'.join(name_parts[:i+1])
            self.log_counts[namespace]['total'] += 1

    def print_summary(self):
        print("====================================================")
        print("=============== Log Messages Summary ===============")
        print("====================================================")

        def print_namespace_summary(namespace, level=0):
            if level > self.print_level:
                return

            indent = ' - ' if level == 0 else '     ' * level
            if level > 0:
                indent += '|-----'
            print(f"{indent}{namespace.split('.')[-1]}: {self.log_counts[namespace]['total']}")
            
            sub_namespaces = sorted(
                [ns for ns in self.log_counts.keys() if ns.startswith(f"{namespace}.") and ns.count('.') == level + 1],
                key=lambda x: self.log_counts[x]['total'],
                reverse=True
            )
            for sub_namespace in sub_namespaces:
                print_namespace_summary(sub_namespace, level + 1)

        root_namespaces = sorted(
            [ns for ns in self.log_counts.keys() if ns.count('.') == 0],
            key=lambda x: self.log_counts[x]['total'],
            reverse=True
        )
        for i, root_namespace in enumerate(root_namespaces):
            if i > 0:
                print("")  # Add a newline between root namespaces
            print_namespace_summary(root_namespace, level=0)

        print("====================================================\n")

def main(args=None):
    parser = argparse.ArgumentParser(description='Rosout Logger')
    parser.add_argument('--level', type=int, default=2, help='Limit the printed level')
    node_args = parser.parse_args()

    rclpy.init(args=args)
    rosout_logger = RosoutLogger(print_level=node_args.level)
    rclpy.spin(rosout_logger)
    rosout_logger.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
