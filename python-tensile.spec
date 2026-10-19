# Tensile GEMM auto-tuner generator (TheRock 10.1)
# Pure Python + C++ sources used at consumer build time (rocBLAS). No prebuilt kernels.

Name:		python-tensile
Version:	10.1.0
Release:	1
Summary:	ROCm Tensile GEMM kernel generator
License:	MIT
Group:		Development/Python
URL:		https://github.com/ROCm/Tensile
Source0:	https://github.com/ROCm/rocm-libraries/releases/download/therock-10.1/tensile.tar.gz#/tensile-%{version}.tar.gz
# Make find_package(Tensile) work with system PATH layout
Patch0:		0001-tensile-config-system-paths.patch
# LLVM 23 true16: GFX11+ f16 cvt needs .l/.h selectors
Patch1:		0002-true16-f16-cvt-llvm23.patch

BuildArch:	noarch
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	pkgconfig(python3)
Requires:	python%{pyver}dist(pyyaml)
Requires:	python%{pyver}dist(msgpack)
Requires:	python%{pyver}dist(joblib)
Requires:	python%{pyver}dist(rich)

Provides:	python3-tensile = %{EVRD}
Provides:	tensile = %{EVRD}
Provides:	cmake(Tensile) = 4.47.0

%description
Tensile generates optimized GEMM and tensor-contraction kernels for AMD GPUs.
This package ships the pure-Python generator and C++ host library sources used
at build time by rocBLAS. No prebuilt code objects are included.

%prep
%autosetup -n tensile -p1

%build
%py3_build

%install
%py3_install
# CMake package for find_package(Tensile) — setuptools data_files land poorly under FHS
# Use share/cmake so a noarch package is multi-lib friendly
mkdir -p %{buildroot}%{_datadir}/cmake/Tensile
install -m 644 Tensile/cmake/TensileConfig.cmake \
	Tensile/cmake/TensileConfigVersion.cmake \
	%{buildroot}%{_datadir}/cmake/Tensile/
# Drop non-FHS cmake install from setuptools data_files
rm -rf %{buildroot}/usr/cmake
# Ensure console scripts are present (setuptools entry_points)
if [ ! -x %{buildroot}%{_bindir}/TensileGetPath ]; then
	mkdir -p %{buildroot}%{_bindir}
	cat > %{buildroot}%{_bindir}/TensileGetPath <<'PY'
#!/usr/bin/python
from Tensile import PrintTensileRoot
PrintTensileRoot()
PY
	chmod 755 %{buildroot}%{_bindir}/TensileGetPath
fi

%files
%license LICENSE.md
%doc README.md CHANGELOG.md
%{python3_sitelib}/Tensile/
%{python3_sitelib}/Tensile-*.egg-info/
%{_bindir}/Tensile
%{_bindir}/TensileCreateLibrary
%{_bindir}/TensileGetPath
%{_bindir}/tensileBenchmarkLibraryClient
%{_bindir}/TensileBenchmarkCluster
%{_bindir}/TensileRetuneLibrary
%{_datadir}/cmake/Tensile/
# setuptools also drops a non-FHS /usr/cmake copy — drop it
%exclude /usr/cmake
