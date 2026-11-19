use base::config::keys;
use hbb_common::config;

const SERVER: &str = "194.32.230.200";
const KEY: &str = "S8ma9SvLwUzl2SQoeXrjpkHD47jt0vanrF3igOZJfmQ=";

// Official update checks would offer the stock RustDesk build, which drops this branding.
pub const UPDATES_DISABLED: bool = true;

// The hidden connection window is otherwise honoured only for Pro or renamed builds.
pub const HIDE_CM_ALLOWED: bool = true;

// Not in `keys`: only `hbb_common::password_security::hide_cm` reads it.
const OPTION_ALLOW_HIDE_CM: &str = "allow-hide-cm";

// Overwrite settings win over the user's config and lock the matching UI controls,
// so employees cannot point the client elsewhere or bring back the connection window.
pub fn apply() {
    let overwrite = [
        (keys::OPTION_CUSTOM_RENDEZVOUS_SERVER, SERVER),
        (keys::OPTION_RELAY_SERVER, SERVER),
        (keys::OPTION_KEY, KEY),
        (keys::OPTION_APPROVE_MODE, "password"),
        (keys::OPTION_VERIFICATION_METHOD, "use-permanent-password"),
        (OPTION_ALLOW_HIDE_CM, "Y"),
        (keys::OPTION_ALLOW_AUTO_UPDATE, "N"),
    ];
    let mut settings = config::OVERWRITE_SETTINGS.write().unwrap();
    for (k, v) in overwrite {
        settings.insert(k.to_owned(), v.to_owned());
    }
    drop(settings);

    config::OVERWRITE_LOCAL_SETTINGS
        .write()
        .unwrap()
        .insert(keys::OPTION_ENABLE_CHECK_UPDATE.to_owned(), "N".to_owned());

    let builtin = [
        keys::OPTION_HIDE_NETWORK_SETTINGS,
        keys::OPTION_HIDE_SERVER_SETTINGS,
        keys::OPTION_HIDE_PROXY_SETTINGS,
        keys::OPTION_HIDE_SECURITY_SETTINGS,
        keys::OPTION_HIDE_STOP_SERVICE,
        keys::OPTION_HIDE_HELP_CARDS,
        keys::OPTION_DISABLE_CHANGE_ID,
    ];
    let mut settings = config::BUILTIN_SETTINGS.write().unwrap();
    for k in builtin {
        settings.insert(k.to_owned(), "Y".to_owned());
    }
}
