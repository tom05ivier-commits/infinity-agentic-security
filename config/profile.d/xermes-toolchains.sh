# Xermes toolchain paths
case ":${PATH:-}:" in
  *:/usr/local/go/bin:*) ;;
  *) export PATH="${PATH:-/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin}:/usr/local/go/bin:/root/.cargo/bin" ;;
esac
