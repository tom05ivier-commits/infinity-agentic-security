case ":${PATH:-}:" in
    *:/usr/local/lib/nodejs/current/bin:*) ;;
    *) export PATH="/usr/local/lib/nodejs/current/bin:${PATH:-}" ;;
esac
