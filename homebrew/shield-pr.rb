# Homebrew formula for Code Review Assistant
# Formula documentation: https://docs.brew.sh/Formula-Cookbook
# Installation: brew install kietnguyenvulcanlabs/tap/shield-pr

class CodeReviewAssistant < Formula
  desc "AI-powered code review CLI using LangChain + Gemini"
  homepage "https://github.com/kietnguyenvulcanlabs/shield-pr"
  url "https://github.com/kietnguyenvulcanlabs/shield-pr/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "AUTO"  # Will be calculated on release
  license "MIT"

  depends_on "python@3.11"

  resource "requirements" do
    # Pin specific versions for stability
    url "https://raw.githubusercontent.com/kietnguyenvulcanlabs/shield-pr/v0.1.0/pyproject.toml"
    sha256 "AUTO"
  end

  def install
    # Install via pip
    python3 = Formula["python@3.11"].opt_bin/"python3.11"

    # Create virtualenv in prefix
    system python3, "-m", "venv", libexec/"venv"

    # Install package
    system libexec/"venv/bin/pip", "install", "--upgrade", "pip"
    system libexec/"venv/bin/pip", "install", *std_pip_args(buildpath)

    # Create wrapper script
    bin.install libexec/"venv/bin/shield-pr" => "shield-pr"
  end

  def caveats
    <<~EOS
      To get started, you need a Gemini API key:
        https://makersuite.google.com/app/apikey

      Set your API key:
        export CRA_API_KEY="your-api-key"

      Or create a config file:
        mkdir -p ~/.config/shield-pr
        echo 'api:
          api_key: your-api-key' > ~/.config/shield-pr/config.yaml

      Run a review:
        shield-pr review src/app.py

      Docker usage:
        docker pull ghcr.io/kietnguyenvulcanlabs/shield-pr:latest
        docker run -v $(pwd):/workspace -e CRA_API_KEY=$CRA_API_KEY \\
          ghcr.io/kietnguyenvulcanlabs/shield-pr:latest review .

      Conda usage:
        conda install -c conda-forge shield-pr
    EOS
  end

  test do
    # Test basic command
    assert_match "Code Review Assistant", shell_output("#{bin}/shield-pr version")

    # Test platforms command
    assert_match "android", shell_output("#{bin}/shield-pr platforms")

    # Test help
    assert_match "AI-powered", shell_output("#{bin}/shield-pr --help")
  end
end
