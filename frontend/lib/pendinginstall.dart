import 'package:flutter/material.dart';

class PendingInstallScreen extends StatelessWidget {
  const PendingInstallScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Pin Location")),
      body: const Center(child: Text("Pending Install Screen")),
    );
  }
}
