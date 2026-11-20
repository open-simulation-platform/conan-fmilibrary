#include <fmilib.h>

#include <cstring>

int main() {
    fmi_import_context_t* c = fmi_import_allocate_context(jm_get_default_callbacks());
    int e = (c == nullptr) ? 1 : 0;
    fmi_import_free_context(c);
#if defined(__APPLE__) && defined(__aarch64__)
    // FMI 2 binaries for Apple silicon are in binaries/aarch64-darwin
    if (std::strcmp(FMI2_PLATFORM, "aarch64-darwin") != 0) e = 1;
#endif
    return e;
}
