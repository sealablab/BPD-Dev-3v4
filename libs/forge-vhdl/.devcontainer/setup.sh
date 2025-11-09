#!/bin/bash
set -e

echo "=========================================="
echo "VHDL-FORGE 3.0 Environment Setup"
echo "=========================================="

# Install GHDL dependencies
echo "📦 Installing GHDL dependencies..."
apt-get update -qq
apt-get install -y -qq \
    llvm-14 \
    libllvm14 \
    gnat \
    gcc \
    make \
    wget \
    ca-certificates

# Download and install GHDL from official release
echo "⬇️  Downloading GHDL 4.1.0..."
cd /tmp
wget -q https://github.com/ghdl/ghdl/releases/download/v4.1.0/ghdl-gha-ubuntu-22.04-llvm.tgz

echo "📂 Installing GHDL..."
tar -xzf ghdl-gha-ubuntu-22.04-llvm.tgz
cp -r ghdl-gha-ubuntu-22.04-llvm/usr/local/* /usr/local/
ldconfig

# Verify GHDL installation
echo "✅ GHDL installed successfully:"
ghdl --version

# Install uv (Python package manager)
echo "📦 Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Run cloud setup script
echo "🔧 Running forge-vhdl cloud setup..."
if [ -f "scripts/cloud_setup_with_ghdl.py" ]; then
    uv run python scripts/cloud_setup_with_ghdl.py
else
    echo "⚠️  Warning: scripts/cloud_setup_with_ghdl.py not found, skipping"
fi

echo "=========================================="
echo "✅ VHDL-FORGE 3.0 Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Run environment detection: uv run python .claude/env_detect.py"
echo "  2. Start workflow: /forge-start"
echo "  3. List available tests: uv run python cocotb_tests/run.py --list"
echo ""
